"""Notification provider configuration and dry-run contract. No network delivery."""
from copy import deepcopy
from urllib.parse import urlsplit
from errors import unprocessable
from security import encrypt_field

DEFAULTS={'smtp_host':'','smtp_port':465,'smtp_username':'','smtp_sender':'','smtp_security':'ssl',
          'sms_url':'','sms_sender':'','sms_template_id':'','mode':'configuration_only'}
SECRETS=('smtp_password','sms_api_key')


def update_config(current, patch):
    if not isinstance(patch,dict) or set(patch)-set(DEFAULTS)-set(SECRETS):
        raise unprocessable('投递配置包含未知字段')
    result={**DEFAULTS,**deepcopy(current)}
    for name,value in patch.items():
        if name=='smtp_port':
            if type(value) is not int or not 1<=value<=65535: raise unprocessable('SMTP 端口无效')
        elif not isinstance(value,str): raise unprocessable('投递配置须为文字')
    if patch.get('mode',DEFAULTS['mode'])!='configuration_only':
        raise unprocessable('本版本仅配置，不启用实际邮件或短信投递')
    if patch.get('smtp_security','ssl') not in ('ssl','starttls'):
        raise unprocessable('SMTP 仅支持 SSL 或 STARTTLS')
    if any('\n' in str(v) or '\r' in str(v) for v in patch.values()):
        raise unprocessable('投递配置不得包含换行')
    next_cfg={**result,**{k:v for k,v in patch.items() if k not in SECRETS}}
    if next_cfg['sms_url']:
        url=urlsplit(next_cfg['sms_url'])
        if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise unprocessable('短信接口须为不含凭据或查询参数的 HTTPS 地址')
    for secret, destination in [('smtp_password',('smtp_host','smtp_port','smtp_username')),('sms_api_key',('sms_url',))]:
        if result.get(secret+'_enc') and any(next_cfg.get(k)!=result.get(k) for k in destination) and secret not in patch:
            raise unprocessable('更换投递地址或账号时请重新填写或清除对应密钥')
        if secret in patch:
            next_cfg[secret+'_enc']=encrypt_field(patch[secret]) if patch[secret] else ''
    return next_cfg


def public_config(value):
    result={**DEFAULTS,**deepcopy(value)}
    for secret in SECRETS:
        result[secret+'_set']=bool(result.pop(secret+'_enc',None))
        result.pop(secret,None)
    return result


def check_config(value):
    public=public_config(value)
    missing_email=[k for k in ('smtp_host','smtp_username','smtp_sender','smtp_password_set') if not public.get(k)]
    missing_sms=[k for k in ('sms_url','sms_sender','sms_template_id','sms_api_key_set') if not public.get(k)]
    return {'mode':'configuration_only','sent':False,'email_ready':not missing_email,'sms_ready':not missing_sms,
            'missing_email':missing_email,'missing_sms':missing_sms,'message':'仅检查已保存配置；未连接服务、未发送邮件或短信'}


def prepare_delivery(channel, recipient, title, content, config):
    """Stable adapter boundary for later provider integration; explicitly dry-run."""
    if channel not in ('email','sms'): raise unprocessable('未知投递渠道')
    return {'channel':channel,'sent':False,'status':'CONFIGURATION_ONLY',
            'configured':check_config(config)[channel+'_ready']}
