from dateutil.relativedelta import relativedelta
from tests.test_review_regressions import test_engine, case, as_client, material
from utils import now


def test_confirmed_retention_is_traceable_and_empty_pages_clamp(case,as_client):
    c=case; m,v=material(c)
    v.uploaded_at=now()-relativedelta(years=11); c.db.flush()
    client=as_client(c.org); url='/api/settings/retention/materials'
    response=client.post(f'{url}/{v.id}/keep',json={'reason':'原件仍需核查'})
    assert response.status_code==200,response.text
    pending=client.get(url+'?page=2').json()['data']
    assert pending['total']==0 and pending['page']==1
    confirmed=client.get(url+'?status=confirmed').json()['data']['items'][0]
    assert confirmed['confirmation']['reason']=='原件仍需核查'
    assert confirmed['confirmation']['confirmed_by']=='org'
    assert confirmed['confirmation']['confirmed_at']
    assert 'stored_path' not in confirmed
