"""User-management scope must be enforced beyond the form's organization picker."""
from copy import deepcopy
import json

import pytest

from errors import AppError
from models import AuditLog, Org, User, UserRole
from services.users import create_user, update_user
from tests.pg_fixtures import pg_schema, case, as_client
from utils import now


def outside_branch(c):
    college = c.add(Org, name='其他学院', org_type='COLLEGE', parent_id=c.school.id,
                    created_at=now(), updated_at=now())
    return c.add(Org, name='其他学院支部', org_type='BRANCH', parent_id=college.id,
                 created_at=now(), updated_at=now())


def target(c, *, org_id=None, role='SYS_ADMIN'):
    user = c.add(User, username='scope_target', real_name='虚构测试用户', password_hash='unchanged-hash',
                 org_id=org_id, is_active=True, must_change_password=False, created_at=now(), updated_at=now())
    c.add(UserRole, user_id=user.id, role=role, org_id=c.school.id, created_at=now())
    return user


def test_college_cannot_create_grant_in_another_college(case):
    foreign = outside_branch(case)
    with pytest.raises(AppError) as error:
        create_user(case.db, case.college_admin, {'username': 'foreign_grant', 'real_name': '虚构用户',
            'org_id': case.branches[0].id, 'roles': [{'role': 'BRANCH_REVIEWER', 'org_id': foreign.id}]})
    assert error.value.status_code == 403
    assert case.db.query(User).filter(User.username == 'foreign_grant').count() == 0


@pytest.mark.parametrize('who', ['student', 'reviewer', 'college_admin'])
def test_orgless_account_password_reset_is_not_public_to_authenticated_users(case, as_client, who):
    user = target(case)
    response = as_client(getattr(case, who)).post(f'/api/users/{user.id}/reset-password')
    assert response.status_code == 403
    assert user.password_hash == 'unchanged-hash' and user.token_version == 0


def test_college_cannot_reset_account_with_higher_grants_in_own_default_org(case, as_client):
    user = target(case, org_id=case.branches[0].id)
    response = as_client(case.college_admin).post(f'/api/users/{user.id}/reset-password')
    assert response.status_code == 403
    assert user.password_hash == 'unchanged-hash'


def test_college_cannot_replace_higher_grants_or_mutate_before_validation(case):
    user = target(case, org_id=case.branches[0].id)
    with pytest.raises(AppError) as error:
        update_user(case.db, case.college_admin, user, {'real_name': '不应写入',
            'roles': [{'role': 'STUDENT', 'org_id': case.branches[0].id}]})
    assert error.value.status_code == 403
    assert user.real_name == '虚构测试用户'
    assert case.db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role == 'SYS_ADMIN').count() == 1


@pytest.mark.parametrize('roles', [[], {}, [None], [{'role': 'INVALID', 'org_id': 1}],
    [{'role': 'STUDENT', 'org_id': True}], ['STUDENT', 'STUDENT']],
    ids=['empty', 'object', 'null-entry', 'unknown-role', 'bool-org', 'duplicate'])
def test_invalid_grants_are_rejected_before_creating_user(case, roles):
    with pytest.raises(AppError) as error:
        create_user(case.db, case.sys_admin, {'username': 'invalid_grants', 'real_name': '虚构用户',
            'org_id': case.branches[0].id, 'roles': deepcopy(roles)})
    assert error.value.status_code == 422
    assert case.db.query(User).filter(User.username == 'invalid_grants').count() == 0


def test_string_false_cannot_enable_a_disabled_user(case):
    user = case.student.user
    user.is_active = False
    case.db.flush()
    with pytest.raises(AppError):
        update_user(case.db, case.org_admin, user, {'real_name': '不应写入', 'is_active': 'false'})
    assert not user.is_active and user.real_name != '不应写入'


def test_user_update_audit_does_not_store_ignored_credentials(case, as_client):
    response = as_client(case.sys_admin).put(f'/api/users/{case.student.id}',
        json={'real_name': '已更新姓名', 'password': 'NeverLogThisPassword9!', 'api_key': 'never-log-key'})
    assert response.status_code == 200
    audit = case.db.query(AuditLog).filter(AuditLog.action == 'USER_UPDATE').order_by(AuditLog.id.desc()).first()
    serialized = json.dumps(audit.detail, ensure_ascii=False)
    assert 'NeverLogThisPassword' not in serialized and 'never-log-key' not in serialized


def test_global_admin_can_manage_orgless_account_and_reset_response_is_not_cached(case, as_client):
    user = target(case)
    response = as_client(case.sys_admin).post(f'/api/users/{user.id}/reset-password')
    assert response.status_code == 200
    assert response.headers.get('cache-control') == 'no-store, private'
    assert user.password_hash != 'unchanged-hash'


def test_college_can_create_update_and_reset_own_ordinary_account(case, as_client):
    user, password = create_user(case.db, case.college_admin, {'username': 'own_account',
        'real_name': '学院内用户', 'org_id': case.branches[0].id,
        'roles': [{'role': 'STUDENT', 'org_id': case.branches[0].id}]})
    assert password and user.must_change_password
    update_user(case.db, case.college_admin, user, {'real_name': '已核对姓名'})
    assert user.real_name == '已核对姓名'
    response = as_client(case.college_admin).post(f'/api/users/{user.id}/reset-password')
    assert response.status_code == 200


def test_self_service_does_not_allow_changing_grants(case):
    user = case.student.user
    update_user(case.db, case.student, user, {'email': 'own@example.invalid', 'is_active': False,
        'roles': [{'role': 'SYS_ADMIN', 'org_id': case.school.id}]})
    assert user.email == 'own@example.invalid' and user.is_active
    assert all(grant.role == 'STUDENT' for grant in user.roles)


@pytest.mark.parametrize('field,value', [('phone', 12345), ('email', {}), ('is_active', 0)])
def test_invalid_profile_values_do_not_partially_apply(case, field, value):
    before = case.student.user.real_name
    with pytest.raises(AppError):
        update_user(case.db, case.org_admin, case.student.user, {'real_name': '不应写入', field: value})
    assert case.student.user.real_name == before
