"""Unusable configuration or absent evidence must not become a passing result."""
from types import SimpleNamespace as N

import pytest

from ai.checks.content import run_content
from ai.checks.format import run_format
from tests.test_priority_repairs import fixture


def evaluate(code, params=None, features=None, *, parsed=True, format_requirements=None, template=None):
    rule,material,parse,kind,rules=fixture(code,params,features=features)
    if format_requirements is not None:
        kind.format_requirements=format_requirements
    if template is not None:
        kind.element_template=template
    args=([material],{material.id:N(id=1)},{1:parse} if parsed else {},{1:kind})
    if code.startswith('R-F'):
        return run_format(None,*args,rule_set=rules)
    return run_content(None,N(archive=N()),*args,False,rule_set=rules)


@pytest.mark.parametrize('value', ['NaN','Infinity',-1,True])
def test_invalid_layout_requirement_never_passes(value):
    assert evaluate('R-F08',{'docx_layout':{'size_pt':value}},{'size_pt':12})[1][0]['result']=='SKIPPED'


@pytest.mark.parametrize('value', ['NaN','Infinity',-1])
def test_invalid_binding_requirement_never_passes(value):
    features={'sections':[{'margins_cm':{'left':2.5}}]}
    assert evaluate('R-F09',{'min_binding_margin_cm':value},features)[1][0]['result']=='SKIPPED'


@pytest.mark.parametrize('code,params', [('R-F06',{'min_chars':[]}),('R-F08',{'docx_layout':[1]}),
                                        ('R-F09',[1])])
def test_malformed_rule_shapes_skip_without_crashing(code,params):
    assert evaluate(code,params,{'size_pt':12})[1][0]['result']=='SKIPPED'


def test_unmeasured_layout_and_direction_never_claim_compliance():
    assert evaluate('R-F08',{'docx_layout':{'size_pt':12}},{'size_pt':'NaN'})[1][0]['result']=='SKIPPED'
    assert evaluate('R-F09',{'orientation':'portrait'},{'sections':[{}]})[1][0]['result']=='SKIPPED'


@pytest.mark.parametrize('code', ['R-C01','R-C03','R-C04','R-C05','R-C06'])
def test_missing_parse_cannot_pass_content_rules(code):
    assert evaluate(code,parsed=False)[1][0]['result']=='SKIPPED'


@pytest.mark.parametrize('template', [[],[42],[{'required':True,'name':'正文','keywords':42}]])
def test_missing_or_malformed_required_elements_skip(template):
    assert evaluate('R-C05',template=template)[1][0]['result']=='SKIPPED'


def test_no_comparable_identity_fields_skip_instead_of_pass():
    assert evaluate('R-C06')[1][0]['result']=='SKIPPED'


@pytest.mark.parametrize('code', ['R-F01','R-F02','R-F03','R-F04','R-F05'])
def test_unconfigured_or_unmeasured_format_rules_skip(code):
    assert evaluate(code)[1][0]['result']=='SKIPPED'
