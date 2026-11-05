"""Opt-in HTTP regression on an EMPTY TEST application, never production.

TEST_ADMIN_PASSWORD=... python tests/e2e_review_flow.py --base-url ...
    --allow-test-writes --output result.json
Creates demo records and one synthetic development archive; does not reset data.
"""
import argparse
from io import BytesIO
import json
import os
from pathlib import Path
import time
from uuid import uuid4

import httpx
from docx import Document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--allow-test-writes", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.allow_test_writes:
        parser.error("This writes test records. Explicit --allow-test-writes is required.")
    checks, requests = [], []
    client = httpx.Client(base_url=args.base_url, timeout=60, trust_env=False)

    def require(name, condition):
        checks.append({"name": name, "passed": bool(condition)})
        assert condition, name

    def call(method, path, actor=None, expected=200, **kwargs):
        headers = {"X-Requested-With": "party-review", **(actor or {})}
        client.cookies.clear()
        response = client.request(method, "/api" + path, headers=headers, **kwargs)
        requests.append({"method": method, "path": path, "status": response.status_code})
        assert response.status_code == expected, (method, path, response.status_code, response.text[:600])
        return response.json().get("data")

    def login(username, password, role=None):
        data = call("POST", "/auth/login", json={"username": username, "password": password})
        roles = data["user"]["roles"]
        selected = next((r for r in roles if r["role"] == role), roles[0])
        cookie = client.cookies.get("prw_session")
        assert cookie, "login must set the HttpOnly session cookie"
        return {"Cookie": "prw_session=" + cookie,
                "X-Active-Role": f'{selected["role"]}@{selected["org_id"]}'}

    def wait_job(jid, actor):
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            job = call("GET", f"/jobs/{jid}", actor)
            if job["status"] in ("SUCCEEDED", "FAILED", "PARTIAL"):
                require(f"job {jid} succeeded", job["status"] == "SUCCEEDED")
                return job
            time.sleep(0.2)
        raise AssertionError(f"Job {jid} timed out")

    try:
        require("health reports database ok", call("GET", "/health")["db"] == "ok")
        call("GET", "/archives", expected=401)
        admin = login("admin", os.environ["TEST_ADMIN_PASSWORD"], "SYS_ADMIN")
        seeded = call("POST", "/admin/seed-demo", admin, json={"reset": False, "run_checks": True})
        require("demo archives created", seeded.get("archives", 24) == 24)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            jobs = call("GET", "/jobs?page_size=200", admin)["items"]
            if all(j["status"] not in ("QUEUED", "RUNNING") for j in jobs):
                require("all initial demo jobs succeeded", all(j["status"] == "SUCCEEDED" for j in jobs))
                break
            time.sleep(0.5)
        else:
            raise AssertionError("Initial demo jobs timed out")
        org = login("demo_org", "Demo@2026")
        branch = login("demo_branch1", "Demo@2026", "BRANCH_REVIEWER")
        cross = login("demo_branch2", "Demo@2026", "CROSS_REVIEWER")
        college = login("demo_college1", "Demo@2026")
        own = call("GET", "/auth/me", branch)
        branch_id = own["active_role"]["org_id"]
        batch_id = call("GET", "/batches", org)["items"][0]["id"]
        student_no = "R" + uuid4().hex[:12]
        created = call("POST", "/archives", org, json={
            "student": {"student_no": student_no, "real_name": "回归测试学生", "birth_date": "2003-05-12"},
            "branch_id": branch_id, "batch_id": batch_id, "current_stage": 1})
        aid = created["archive"]["id"]
        sid = created["archive"]["submissions"][0]["id"]
        student = login(student_no, created["initial_password"])
        call("GET", f"/submissions/{sid}", student, expected=403)
        call("PUT", "/auth/password", student, json={"old_password": created["initial_password"], "new_password": "Regression@2026"})
        student = login(student_no, "Regression@2026")
        require("new archive starts in draft", call("GET", f"/submissions/{sid}", student)["status"] == "DRAFT")
        doc = Document()
        for paragraph in ["入党申请书", "敬爱的党组织：", "姓名：回归测试学生", "申请人：回归测试学生", "2023年3月15日", "此致", "敬礼！"]:
            doc.add_paragraph(paragraph)
        stream = BytesIO()
        doc.save(stream)
        uploaded = call("POST", f"/archives/{aid}/materials", student,
                        files={"file": ("申请书.docx", stream.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
        mid = uploaded["material"]["id"]
        wait_job(uploaded["parse_job_id"], student)
        parsed = call("GET", f"/materials/{mid}/parsed", student)
        require("DOCX text parsed", "回归测试学生" in parsed["full_text"])
        require("anonymous material download denied", client.get(f"/api/materials/{mid}/file").status_code == 401)
        require("authenticated preview renders", client.get(f"/api/materials/{mid}/pages/1", headers=student).status_code == 200)
        job = call("POST", f"/submissions/{sid}/ai-check", student, json={"use_llm": False})
        wait_job(job["job_id"], student)
        sub = call("GET", f"/submissions/{sid}", student)
        require("fresh AI report is usable", sub["latest_report"] and not sub["latest_report"]["is_stale"])
        issues = call("GET", f"/submissions/{sid}/issues", student)["items"]
        for issue in issues:
            if issue["severity"] == "BLOCK":
                call("PUT", f'/issues/{issue["id"]}/response', student, json={
                    "response_type": "EXPLAINED", "response_text": "自动化测试样例，已逐项核对并记录缺少的材料"})
        sub = call("POST", f"/submissions/{sid}/submit", student, json={})["submission"]
        require("student submits to branch", sub["status"] == "BRANCH_REVIEW")
        call("POST", f"/reports/{sub['latest_report']['id']}/handover", college,
             expected=403, json={"human_decision": "CONFIRM", "handover_reason": "越级接管应拒绝"})
        returned = call("POST", f"/submissions/{sid}/review", branch, json={
            "level": "BRANCH", "decision": "return", "comment": "自动化测试：请补全材料后重新提交"})
        require("return produces notice", returned["submission"]["status"] == "RETURNED" and returned["notice_id"])
        resubmitted = call("POST", f"/submissions/{sid}/submit", student, json={})
        require("resubmit keeps return level and increments round", resubmitted["submission"]["status"] == "BRANCH_REVIEW" and resubmitted["submission"]["round_no"] == 2)
        wait_job(resubmitted["recheck_job_id"], student)
        sub = call("GET", f"/submissions/{sid}", branch)
        require("automatic recheck report is fresh", not sub["latest_report"]["is_stale"])
        issues = call("GET", f"/submissions/{sid}/issues", branch)["items"]
        for issue in issues:
            call("PUT", f'/issues/{issue["id"]}', branch, json={"action": "reject", "note": "仅用于验证状态机的合成测试，不作为真实材料审核结论"})
        rid = sub["latest_report"]["id"]
        call("POST", f"/reports/{rid}/handover", branch, expected=422,
             json={"human_decision": "CONFIRM", "handover_reason": ""})
        call("POST", f"/reports/{rid}/handover", branch, json={
            "human_decision": "OVERRIDE_PASS" if issues else "CONFIRM",
            "handover_reason": "合成测试已核实状态机，本操作仅供自动化回归验证", "issue_ids": [i["id"] for i in issues]})
        require("handover completes", not call("GET", f"/submissions/{sid}", branch)["can"]["handover"])
        for role_actor, level, expected in [(branch, "BRANCH", "CROSS_REVIEW"), (cross, "CROSS", "COLLEGE_REVIEW"), (college, "COLLEGE", "ORG_FILING")]:
            reviewed = call("POST", f"/submissions/{sid}/review", role_actor, json={"level": level, "decision": "pass", "report_id": rid})
            require(level + " review advances", reviewed["submission"]["status"] == expected)
        filed = call("POST", f"/submissions/{sid}/filing", org, json={"comment": "合成回归测试归档"})
        require("filing advances archive to stage 2", filed["submission"]["status"] == "FILED" and filed["archive"]["current_stage"] == 2 and filed["next_submission_id"])
        call("PUT", f"/materials/{mid}/type", org, expected=403, json={"material_type_id": 1})
        require("review trail records full chain", len(call("GET", f"/submissions/{sid}/review-records", org)) >= 7)
        require("unknown API remains 404", client.get("/api/not-an-api").status_code == 404)
        require("SPA routes remain available", client.get("/review/tasks").status_code == 200)
    except Exception as exc:
        checks.append({"name": "complete HTTP flow", "passed": False, "error": str(exc)})
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"checks": checks, "http_requests": requests,
            "passed": sum(x["passed"] for x in checks), "failed": sum(not x["passed"] for x in checks)}, ensure_ascii=False, indent=2), encoding="utf-8")
        client.close()
        print(json.dumps({"passed": sum(x["passed"] for x in checks), "failed": sum(not x["passed"] for x in checks), "requests": len(requests)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
