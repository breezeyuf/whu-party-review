from unittest.mock import Mock
import httpx
import pytest

from services import model_network as policy
from services import cas
from errors import AppError


@pytest.mark.parametrize('url', ['https://8.8.8.8/v1', 'http://169.254.169.254/latest',
    'http://0.0.0.0/v1', 'http://10.0.0.1:0/v1', 'http://[fe80::1]/v1', 'http://[::ffff:8.8.8.8]/v1',
    'http://user:pass@10.0.0.1/v1', 'file:///etc/passwd', 'https://10.0.0.1/v1?x=1',
    'http://[::1%25lo]/v1', 'http://10.0.0.1:99999/v1', 'https://[bad', 'http://10.0.0.1\\@8.8.8.8'])
def test_forbidden_model_destinations(url):
    with pytest.raises(AppError):
        policy.destination(url)


@pytest.mark.parametrize('url', ['http://127.0.0.1:8001/v1', 'https://10.1.2.3/v1',
    'http://172.16.0.1/v1', 'http://192.168.1.2/v1', 'http://[::1]/v1', 'https://[fd12::1]/v1'])
def test_private_destinations_allowed(url):
    assert policy.destination(url)[1]


def test_dns_all_addresses_must_be_private(monkeypatch):
    monkeypatch.setattr(policy, '_resolve', lambda *args: ['10.0.0.1', '8.8.8.8'])
    with pytest.raises(AppError):
        policy.destination('https://campus.example/v1')
    monkeypatch.setattr(policy, '_resolve', lambda *args: ['10.0.0.1', 'fd00::1'])
    assert policy.destination('https://campus.example/v1')[1] == '10.0.0.1'


def test_transport_pins_verified_ip_and_keeps_host_and_tls_name(monkeypatch):
    resolver = Mock(return_value=['10.1.2.3'])
    monkeypatch.setattr(policy, '_resolve', resolver)
    transport = policy.PrivateModelTransport()
    captured = []
    transport.transport.close()
    transport.transport = httpx.MockTransport(lambda r: captured.append(r) or httpx.Response(200))
    with httpx.Client(transport=transport, trust_env=False) as client:
        assert client.post('https://model.school.test/v1/chat/completions', json={}).status_code == 200
    request = captured[0]
    assert request.url.host == '10.1.2.3'
    assert request.headers['host'] == 'model.school.test'
    assert request.extensions['sni_hostname'] == 'model.school.test'
    resolver.assert_called_once()


def test_actual_model_boundary_blocks_public_before_sending(monkeypatch):
    from ai import llm
    client = Mock()
    monkeypatch.setattr(llm.httpx, 'Client', client)
    response, error = llm._post_chat('https://8.8.8.8/v1', {}, {'Authorization': 'Bearer synthetic'}, 1, 1)
    assert response is None and '私网' in error
    client.assert_not_called()


def test_dns_change_at_send_time_is_rechecked(monkeypatch):
    from ai import llm
    values = iter([['10.1.2.3'], ['8.8.8.8']])
    monkeypatch.setattr(policy, '_resolve', lambda *args: next(values))
    response, error = llm._post_chat('https://campus.test/v1', {}, {}, 1, 1)
    assert response is None and '私网' in error


@pytest.mark.parametrize('xml', [
    '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas"><cas:authenticationFailure/></cas:serviceResponse>',
    '<!DOCTYPE test [<!ENTITY x "expanded">]><test>&x;</test>',
    '<serviceResponse><authenticationSuccess><user>admin</user></authenticationSuccess></serviceResponse>',
    '<not-xml', 'x' * 65537,
], ids=['failure', 'entity', 'wrong-namespace', 'malformed', 'oversize'])
def test_cas_rejects_invalid_or_unsafe_responses(monkeypatch, xml):
    client_type = httpx.Client
    transport = httpx.MockTransport(lambda r: httpx.Response(200, text=xml))
    monkeypatch.setattr(cas.httpx, 'Client', lambda **kw: client_type(transport=transport, **kw))
    with pytest.raises(AppError):
        cas.validate_ticket({'validate_url': 'https://cas.test/serviceValidate'}, 'ST-test', 'https://app.test/callback')


def test_cas_validates_exact_service_and_ticket_over_tls(monkeypatch):
    seen = []
    xml = '<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas"><cas:authenticationSuccess><cas:user>2026123456</cas:user></cas:authenticationSuccess></cas:serviceResponse>'
    client_type = httpx.Client
    transport = httpx.MockTransport(lambda r: seen.append(r) or httpx.Response(200, text=xml))
    monkeypatch.setattr(cas.httpx, 'Client', lambda **kw: client_type(transport=transport, **kw))
    assert cas.validate_ticket({'validate_url': 'https://cas.test/serviceValidate'}, 'ST-test', 'https://app.test/callback?state=x') == '2026123456'
    assert seen[0].url.params['service'] == 'https://app.test/callback?state=x'
    assert seen[0].url.params['ticket'] == 'ST-test'
