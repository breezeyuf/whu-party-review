"""Check/apply authentication configuration from an operator's trusted shell."""
import argparse
import json
import os
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['demo', 'sso'], required=True)
    parser.add_argument('--login-url')
    parser.add_argument('--validate-url')
    parser.add_argument('--apply', action='store_true', help='Save and revoke existing sessions; default is validation only')
    args = parser.parse_args()
    if not os.environ.get('DATABASE_URL'):
        parser.error('必须显式设置 DATABASE_URL，拒绝使用默认数据库')
    from database import SessionLocal
    from services.sessions import auth_config, validate_auth_config
    from services.settings import update_settings
    from services.audit import log
    with SessionLocal() as db:
        patch = {'mode': args.mode}
        if args.login_url is not None:
            patch['login_url'] = args.login_url
        if args.validate_url is not None:
            patch['validate_url'] = args.validate_url
        validate_auth_config({**auth_config(db), **patch})
        if args.apply:
            update_settings(db, SimpleNamespace(role='SYS_ADMIN', id=None), {'auth': patch})
            log(db, None, 'AUTH_CONFIG_OPERATOR', 'settings', None, {'mode': args.mode})
            db.commit()
        print(json.dumps({'valid': True, 'applied': args.apply, 'mode': args.mode}, ensure_ascii=False))


if __name__ == '__main__':
    main()
