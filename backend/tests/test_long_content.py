import json
from ai import llm
from tests.test_llm_credentials import endpoint


def test_full_text_is_chunked_through_the_tail_and_deduplicated(endpoint):
    db,config,_,requests=endpoint
    source='开头'+('甲'*13000)+'尾部独有证据'
    result,error,_=llm.chat_json(db,'CONTENT_CHECK',{'text':source,'timeline':{'T01':{'date':'2020-01-01'}}})
    assert error is None and result=={'issues':[]}
    assert len(requests)==3
    payloads=[json.loads(r.content) for r in requests]
    assert '尾部独有证据' in payloads[-1]['messages'][1]['content']
    assert all('2020-01-01' in p['messages'][1]['content'] for p in payloads)


def test_excessive_length_is_explicit_failure_not_truncated_pass(endpoint):
    db,_,_,requests=endpoint
    result,error,_=llm.chat_json(db,'CONTENT_CHECK',{'text':'长'*200000})
    assert result is None and error and not requests
