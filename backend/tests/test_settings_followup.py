"""Configuration failures must be actionable, without sending notifications."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from errors import AppError
from services import delivery, settings


@pytest.mark.parametrize('url', ['https://[bad', 'https://sms.invalid:bad/send',
                                  'https://sms.invalid:99999/send', 'https://sms.invalid:0/send',
                                  'https://sms.invalid /send'])
def test_malformed_delivery_url_is_validation_error(url):
    with pytest.raises(AppError):
        delivery.update_config({}, {'sms_url':url})


def test_delivery_whitespace_and_clearing_do_not_report_ready():
    config=delivery.update_config({}, {'smtp_host':'  ', 'sms_sender':'  '})
    assert config['smtp_host']=='' and config['sms_sender']==''
    assert delivery.check_config({'smtp_host':'  ', 'smtp_username':'test',
          'smtp_sender':'test@invalid','smtp_password_enc':'encrypted'})['email_ready'] is False
    config=delivery.update_config({'sms_url':'https://sms.invalid/send','sms_api_key_enc':'encrypted'},
                                 {'sms_url':'','sms_api_key':''})
    assert config['sms_url']=='' and not delivery.public_config(config)['sms_api_key_set']
    assert delivery.check_config(config)['sent'] is False


@pytest.mark.parametrize('group', ['delivery','ocr','retention','notification'])
def test_non_object_settings_cannot_succeed_silently(group):
    with pytest.raises(AppError):
        settings.update_settings(Mock(),SimpleNamespace(role='SYS_ADMIN'),{group:[]})


@pytest.mark.parametrize('patch', [{'llm_enabled':'false'}, {'desensitize':0}, {'model':3},
                                  {'timeout_s':0}, {'max_concurrency':1.5}, {'max_concurrency':33},
                                  {'temperature':float('nan')}, {'classify_confidence_threshold':2}])
def test_invalid_model_runtime_settings_are_rejected(patch):
    with pytest.raises(AppError):
        settings.update_settings(Mock(),SimpleNamespace(role='SYS_ADMIN'),{'ai':patch})
