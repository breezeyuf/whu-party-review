import {test} from "node:test"
import assert from "node:assert/strict"
import {issuePresentation} from "../src/utils/issuePresentation.js"

test("missing required dates use names and distinguish unavailable extraction from missing original",()=>{
 const issue={source:"AI_RULE",rule_code:"R-T22",title:"阶段必填节点与单调递增",description:"缺少 T01,T02",actual_value:"缺失 T01,T02",suggestion:"《》中T01为缺失 T01,T02"}
 const display=issuePresentation(issue)
 assert.match(display.title,/必要日期/)
 assert.match(display.description,/出生日期、递交入党申请书日期/)
 assert.match(display.description,/不代表原件一定未填写/)
 assert.doesNotMatch(display.suggestion,/《》|T01|单调递增/)
 assert.equal(issue.description,"缺少 T01,T02")
})
test("metadata names win, chronological errors remain distinct, and manual records stay untouched",()=>{
 const manual={source:"MANUAL",description:"原文《》与T01"}
 assert.equal(issuePresentation(manual),manual)
 assert.match(issuePresentation({rule_code:"R-T22",description:"缺少 T02"},[{code:"T02",name:"申请日期"}]).description,/申请日期/)
 assert.equal(issuePresentation({rule_code:"R-T22",description:"日期顺序颠倒"}).description,"日期顺序颠倒")
 assert.equal(issuePresentation({suggestion:"《》请核实"}).suggestion,"本次提交材料请核实")
})
