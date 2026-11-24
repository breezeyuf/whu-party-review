"""Verify packaged date review via real HTTP uploads, workers and isolated data.

Run with the project Python environment (httpx and python-docx required).
The app must be in an ASCII path and --data-dir must not already exist.
Only synthetic organizations, users and documents are created.
"""
import argparse
import hashlib
import io
import json
import subprocess
import time
import uuid
from pathlib import Path

import httpx
from docx import Document


args = argparse.ArgumentParser()
args.add_argument('--exe', type=Path, required=True)
args.add_argument('--data-dir', type=Path, required=True)
args.add_argument('--output', type=Path, required=True)
a = args.parse_args()
exe, data_dir = a.exe.resolve(), a.data_dir.resolve()
if data_dir.exists() or not exe.is_file() or not str(data_dir).isascii() or not str(exe).isascii():
    raise SystemExit('Require an existing ASCII EXE path and a fresh ASCII data directory.')
checks, failure, proc = [], None, None


def check(name, valid):
    checks.append({'name': name, 'passed': bool(valid)})
    if not valid:
        raise AssertionError(name)


try:
    proc = subprocess.Popen([str(exe), '--headless', '--data-dir', str(data_dir)], creationflags=subprocess.CREATE_NO_WINDOW)
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError('Packaged app exited during startup')
        try:
            cfg = json.loads((data_dir / 'config.json').read_text(encoding='utf-8-sig'))
            base = f"http://127.0.0.1:{cfg['http_port']}"
            with httpx.Client(trust_env=False, timeout=2) as health_client:
                if health_client.get(base + '/api/health').json()['data']['db'] == 'ok':
                    break
        except (OSError, ValueError, KeyError, httpx.HTTPError):
            pass
        time.sleep(.5)
    else:
        raise RuntimeError('Packaged app startup timed out')
    def client():
        return httpx.Client(base_url=base + '/api', trust_env=False, timeout=90,
                            headers={'X-Requested-With': 'party-review', 'Origin': base})
    admin, organization, reviewer = client(), client(), client()
    def request(who, method, path, **kwargs):
        response = who.request(method, path, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f'{method} {path}: HTTP {response.status_code}')
        return response.json()['data']
    def login(who, username, password):
        request(who, 'POST', '/auth/login', json={'username': username, 'password': password})
        new_password = 'Qa9' + uuid.uuid4().hex + '!'
        request(who, 'PUT', '/auth/password', json={'old_password': password, 'new_password': new_password})
        request(who, 'POST', '/auth/login', json={'username': username, 'password': new_password})
    login(admin, 'admin', cfg['admin_password'])
    school = request(admin, 'GET', '/auth/me')['active_role']['org_id']
    org_grant = request(admin, 'POST', '/users', json={'username': 'package_date_org', 'real_name': '虚构组织管理员',
        'org_id': school, 'roles': [{'role': 'ORG_ADMIN', 'org_id': school}]})
    login(organization, 'package_date_org', org_grant['initial_password'])
    college = request(admin, 'POST', '/orgs', json={'name': '虚构日期验收学院', 'org_type': 'COLLEGE', 'parent_id': school})
    branch = request(admin, 'POST', '/orgs', json={'name': '虚构日期验收支部', 'org_type': 'BRANCH', 'parent_id': college['id']})
    batch = request(organization, 'POST', '/batches', json={'name': '虚构日期验收批次', 'year': 2026,
        'start_date': '2026-01-01', 'end_date': '2026-12-31'})
    grant = request(admin, 'POST', '/users', json={'username': 'package_date_reviewer', 'real_name': '虚构审核员',
        'org_id': branch['id'], 'roles': [{'role': 'BRANCH_REVIEWER', 'org_id': branch['id']}]})
    login(reviewer, 'package_date_reviewer', grant['initial_password'])
    types = request(organization, 'GET', '/rules/material-types')
    type_ids = {row['code']: row['id'] for row in types}

    def parsed_case(index, text, *, type_code='TRAINING_CERT', node_code='T10', stage=3):
        arch = request(organization, 'POST', '/archives', json={'branch_id': branch['id'], 'batch_id': batch['id'],
            'current_stage': stage, 'student': {'student_no': f'PACKAGE_DATE_{index}', 'real_name': f'虚构日期学生{index}'}})['archive']
        doc = Document()
        for line in text.splitlines():
            doc.add_paragraph(line)
        content = io.BytesIO()
        doc.save(content)
        uploaded = request(reviewer, 'POST', f"/archives/{arch['id']}/materials",
            data={'stage_code': str(stage), 'material_type_id': str(type_ids[type_code])},
            files={'file': ('training.docx', content.getvalue(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')})
        wait_job(uploaded['parse_job_id'])
        mid = uploaded['material']['id']
        parsed = request(reviewer, 'GET', f'/materials/{mid}/parsed')
        rows = [row for row in parsed['extractions'] if row['node_code'] == node_code]
        return arch, mid, parsed, rows

    def wait_job(job_id):
        started = time.monotonic()
        until = time.monotonic() + 120
        while time.monotonic() < until:
            response = reviewer.get(f'/jobs/{job_id}')
            # The HTTP body can arrive just before the request dependency commits
            # its new job. Match the UI's polling behavior, with a short bound;
            # persistent missing/unauthorized jobs must still fail this check.
            if response.status_code == 404 and time.monotonic() - started < 3:
                time.sleep(.1)
                continue
            if response.status_code >= 400:
                raise RuntimeError(f'GET /jobs/{job_id}: HTTP {response.status_code}')
            result = response.json()['data']
            if result['status'] == 'SUCCEEDED':
                return
            if result['status'] in ('FAILED', 'CANCELLED'):
                raise RuntimeError('Real packaged parse job failed')
            time.sleep(.5)
        raise RuntimeError('Real packaged parse job timed out')

    _, _, good_parsed, good = parsed_case(1, '集中培训结业证书\n出生日期：2000年1月1日\n培训时间：2026年9月15日至2026年9月18日，共24学时\n落款：2026年9月20日')
    check('真实 DOCX 上传和后台解析排除出生、落款日期', bool(good) and good[0]['date'] == '2026-09-15' and good[0]['end_date'] == '2026-09-18' and good[0]['usable'])
    check('培训起止和学时映射只生成一条记录', len(good) == 1 and good[0]['hours'] == 24)
    check('培训材料不能提供出生日期节点', all(row['node_code'] != 'T01' for row in good_parsed['extractions']))
    arch, mid, parsed, uncertain = parsed_case(2, '集中培训结业证书\n第一期培训：2026年9月1日至2026年9月3日\n第二期培训：2026年9月20日至2026年9月22日')
    check('多期培训保留独立候选并要求人工确认', len(uncertain) == 2 and all(not row['usable'] for row in uncertain))
    timeline = request(reviewer, 'GET', f"/archives/{arch['id']}/timeline")
    node = next(row for row in timeline['nodes'] if row['code'] == 'T10')
    check('未确认区间不进入有效时间线', node['effective']['date'] is None)
    chosen, other = uncertain
    request(reviewer, 'PUT', f'/materials/{mid}/parsed', json={'version_id': parsed['version_id'],
        'reason': '已核对原始证书，本阶段采用第一期培训，另一组不适用',
        'extractions': [{'extraction_id': chosen['id'], 'date': chosen['date'], 'end_date': chosen['end_date']},
                        {'extraction_id': other['id'], 'delete': True}]})
    confirmed = request(reviewer, 'GET', f'/materials/{mid}/parsed')['extractions']
    confirmed = [row for row in confirmed if row['node_code'] == 'T10']
    check('审核员确认区间后成为有效人工证据', len(confirmed) == 1 and confirmed[0]['usable'] and confirmed[0]['method'] == 'MANUAL')
    retry = request(reviewer, 'POST', f'/materials/{mid}/retry-parse', json={})
    wait_job(retry['parse_job_id'])
    after = request(reviewer, 'GET', f'/materials/{mid}/parsed')['extractions']
    after = [row for row in after if row['node_code'] == 'T10']
    check('真实后台重新解析保留人工确认及删除决定', len(after) == 1 and after[0]['method'] == 'MANUAL' and after[0]['date'] == chosen['date'])
    _, _, _, reverse = parsed_case(3, '集中培训结业证书\n培训时间：2026年9月18日至2026年9月15日')
    check('写反区间保留原顺序且不用于计算', bool(reverse) and reverse[0]['date'] == '2026-09-18' and reverse[0]['end_date'] == '2026-09-15' and not reverse[0]['usable'])
    _, talk_id, talk_parsed, talk = parsed_case(4, '谈话记录\n谈话日期：2026年9月15日',
        type_code='PARTY_TALK_RECORD', node_code='T03', stage=1)
    check('早期谈话不会生成后期党委谈话日期', len(talk) == 1 and talk[0]['usable']
          and all(row['node_code'] != 'T15' for row in talk_parsed['extractions']))
    retag = request(reviewer, 'PUT', f'/materials/{talk_id}/type', json={'material_type_id': type_ids['COMMITTEE_TALK_RECORD']})
    wait_job(retag['parse_job_id'])
    retagged = request(reviewer, 'GET', f'/materials/{talk_id}/parsed')['extractions']
    check('更正材料类型自动触发真实解析并更新日期归属', any(row['node_code'] == 'T15' and row['usable'] for row in retagged)
          and all(row['node_code'] != 'T03' for row in retagged))
    _, _, publicity_parsed, publicity = parsed_case(5, '公示时间：2026年9月15日至2026年9月22日',
        type_code='CANDIDATE_PUBLICITY', node_code='T11')
    check('发展对象公示不会生成转正公示日期', len(publicity) == 1 and publicity[0]['usable']
          and all(row['node_code'] != 'T19' for row in publicity_parsed['extractions']))
    _, _, _, birth = parsed_case(6, '自传\n出生日期：２００３年５月１２日',
        type_code='AUTOBIOGRAPHY', node_code='T01', stage=1)
    check('全角出生日期保留原文并正常生效', bool(birth) and birth[0]['date'] == '2003-05-12'
          and birth[0]['raw_text'] == '２００３年５月１２日' and birth[0]['usable'])
    admin.close()
    organization.close()
    reviewer.close()
except Exception as exc:
    failure = f'{type(exc).__name__}: {exc}'
finally:
    if proc and proc.poll() is None:
        (data_dir / 'stop.request').touch()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=15)
    result = {'checks': checks, 'passed': sum(row['passed'] for row in checks), 'error': failure,
              'exe_sha256': hashlib.sha256(exe.read_bytes()).hexdigest()}
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'error': failure}, ensure_ascii=False))
if failure:
    raise SystemExit(1)
