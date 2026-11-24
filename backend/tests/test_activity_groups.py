import pytest

from models import Job, AuditLog, Org, UserRole
from tests.test_review_regressions import case, test_engine, as_client
from utils import now


def add_job(c, user, status='SUCCEEDED'):
    return c.add(Job, job_type='PARSE', created_by=user.id, target_type='test', status=status, created_at=now(), total=1, done_count=0, failed_count=0, progress=0, attempts=0, max_attempts=3)


def test_creator_aggregation_paginates_people_not_jobs(case, as_client):
    c=case
    other=c.actor('other', 'STUDENT', c.branches[1])
    other.user.real_name=c.student.user.real_name
    for _ in range(25): add_job(c, c.student)
    add_job(c,c.student,'RUNNING')
    add_job(c,other,'FAILED')
    client=as_client(c.org)
    data=client.get('/api/jobs/creators',params={'page_size':1}).json()['data']
    assert data['total']==2 and len(data['items'])==1
    groups=client.get('/api/jobs/creators').json()['data']['items']
    a=next(row for row in groups if row['created_by']==c.student.id)
    assert a['total']==26 and a['running']==1 and a['failed']==0
    assert len({row['created_by'] for row in groups})==2
    rows=client.get('/api/jobs',params={'created_by':c.student.id,'page_size':20,'page':2}).json()['data']
    assert rows['total']==26 and len(rows['items'])==6
    assert all(row['created_by']==c.student.id and row['created_by_username']=='student' for row in rows['items'])
    filtered=client.get('/api/jobs/creators',params={'status':'RUNNING','q':'student'}).json()['data']
    assert filtered['total']==1 and filtered['items'][0]['total']==1


def test_creator_filters_do_not_expand_scope(case, as_client):
    c=case
    add_job(c,c.student)
    add_job(c,c.org)
    client=as_client(c.student)
    data=client.get('/api/jobs/creators').json()['data']
    assert [row['created_by'] for row in data['items']]==[c.student.id]
    assert client.get('/api/jobs',params={'created_by':c.org.id}).json()['data']['total']==0
    reviewer=as_client(c.reviewer)
    assert reviewer.get('/api/jobs/creators').json()['data']['total']==0


def test_audit_actors_search_history_filter_and_permissions(case, as_client):
    c=case
    for uid,username in [(c.student.id,'student'),(c.org.id,'org'),(None,'deleted-old'),(999999,'deleted-id')]:
        c.add(AuditLog,user_id=uid,username=username,role='STUDENT',action='LOGIN',created_at=now())
    client=as_client(c.org)
    data=client.get('/api/audit-logs/actors',params={'page_size':2}).json()['data']
    assert data['total']==4 and len(data['items'])==2
    found=client.get('/api/audit-logs/actors',params={'q':'deleted'}).json()['data']
    assert found['total']==2
    old=next(row for row in found['items'] if row['user_id'] is None)
    rows=client.get('/api/audit-logs',params={'legacy_username':old['legacy_username']}).json()['data']['items']
    assert len(rows)==1 and rows[0]['username']=='deleted-old'
    rows=client.get('/api/audit-logs',params={'user_id':c.student.id}).json()['data']['items']
    assert len(rows)==1 and rows[0]['user_id']==c.student.id
    assert as_client(c.student).get('/api/audit-logs/actors').status_code==403


def test_mark_all_read_changes_current_account_only(case, as_client):
    from models import Message
    c=case
    mine=c.add(Message,user_id=c.student.id,msg_type='SYSTEM',title='mine',is_read=False,created_at=now())
    theirs=c.add(Message,user_id=c.org.id,msg_type='SYSTEM',title='other',is_read=False,created_at=now())
    client=as_client(c.student)
    assert client.put('/api/messages/read-all').json()['data']['updated']==1
    assert client.get('/api/messages/unread-count').json()['data']['count']==0
    c.db.refresh(theirs)
    assert theirs.is_read is False
    assert client.put('/api/messages/read-all').json()['data']['updated']==0


@pytest.mark.parametrize('role', ['STUDENT', 'BRANCH_REVIEWER', 'CROSS_REVIEWER'])
def test_users_role_filter_paginates_unique_users(case, as_client, role):
    c = case
    first = c.actor('role-filter-first', role, c.branches[0])
    c.add(UserRole, user_id=first.id, role=role, org_id=c.branches[1].id, created_at=now())
    second = c.actor('role-filter-second', role, c.branches[0])
    third = c.actor('role-filter-third', role, c.branches[1])
    c.actor('role-filter-unrelated', 'ORG_ADMIN', c.school)
    client = as_client(c.org)

    pages = []
    for page in (1, 2, 3):
        response = client.get('/api/users', params={
            'q': 'role-filter-', 'role': role, 'page': page, 'page_size': 2,
        })
        assert response.status_code == 200
        data = response.json()['data']
        assert data['total'] == 3
        assert data['page'] == page and data['page_size'] == 2
        pages.append(data['items'])

    assert [[row['id'] for row in rows] for rows in pages] == [
        [first.id, second.id], [third.id], [],
    ]
    ids = [row['id'] for rows in pages for row in rows]
    assert len(ids) == len(set(ids)) == 3
    assert {(grant['role'], grant['org_id']) for grant in pages[0][0]['roles']} == {
        (role, c.branches[0].id), (role, c.branches[1].id),
    }


@pytest.mark.parametrize('role', ['BRANCH_REVIEWER', 'CROSS_REVIEWER'])
def test_users_role_filter_preserves_college_scope(case, as_client, role):
    c = case
    other_college = c.add(Org, name='Other college', org_type='COLLEGE', parent_id=c.school.id,
                          created_at=now(), updated_at=now())
    other_branch = c.add(Org, name='Other branch', org_type='BRANCH', parent_id=other_college.id,
                         created_at=now(), updated_at=now())
    local = c.actor('scope-local', role, c.branches[0])
    c.add(UserRole, user_id=local.id, role=role, org_id=c.branches[1].id, created_at=now())
    external_default = c.actor('scope-external-default', role, other_branch)
    c.add(UserRole, user_id=external_default.id, role=role, org_id=c.branches[0].id,
          created_at=now())
    foreign_grant_only = c.actor('scope-foreign-grant-only', role, other_branch)
    foreign_grant_only.user.org_id = c.branches[0].id
    c.actor('scope-outsider', role, other_branch)
    c.actor('scope-wrong-role', 'STUDENT', c.branches[0])
    c.db.flush()
    client = as_client(c.col)

    # Cross-review selectors follow grant scope; other roles follow default organization.
    expected = [local.id, external_default.id if role == 'CROSS_REVIEWER' else foreign_grant_only.id]
    ids = []
    for page in (1, 2, 3):
        response = client.get('/api/users', params={
            'q': 'scope-', 'role': role, 'page': page, 'page_size': 1,
        })
        assert response.status_code == 200
        data = response.json()['data']
        assert data['total'] == len(expected)
        assert data['page'] == page and data['page_size'] == 1
        assert [row['id'] for row in data['items']] == expected[page - 1:page]
        ids.extend(row['id'] for row in data['items'])

    assert ids == expected
    assert len(ids) == len(set(ids))
