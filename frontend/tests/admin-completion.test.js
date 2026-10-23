import test from "node:test"
import assert from "node:assert/strict"
import { normalizeGrants, batchPayload } from "../src/utils/adminWorkflow.js"
import { nodePayload, trialOverrides } from "../src/utils/ruleWorkflow.js"
import { settingsPatch } from "../src/utils/settingsWorkflow.js"

const orgs = [{id:1,org_type:"COLLEGE"},{id:2,org_type:"BRANCH",parent_id:1},{id:3,org_type:"BRANCH",parent_id:1},{id:4,org_type:"BRANCH",parent_id:9}]
test("多组织授权完整保留，同角色不同组织可共存", () => {
  const grants = [{role:"BRANCH_REVIEWER",org_id:"2"},{role:"BRANCH_REVIEWER",org_id:"3"},{role:"COLLEGE_REVIEWER",org_id:1}]
  assert.equal(normalizeGrants(grants,orgs,{role:"ORG_ADMIN"}).length,3)
  assert.throws(() => normalizeGrants([...grants,grants[0]],orgs,{role:"ORG_ADMIN"}),/重复/)
})
test("学院授权不能跨学院或授予管理员，不能删除全部授权", () => {
  const actor = {role:"COLLEGE_REVIEWER",org_id:1}
  assert.throws(() => normalizeGrants([{role:"SYS_ADMIN",org_id:1}],orgs,actor))
  assert.throws(() => normalizeGrants([{role:"BRANCH_REVIEWER",org_id:4}],orgs,actor))
  assert.throws(() => normalizeGrants([],orgs,actor))
})
test("批次五级截止日可保存和清空，并校验真实日期与阶段", () => {
  const form = {id:1,name:"测试",year:2026,stage_codes:"1,2",start_date:"2026-01-01",end_date:"2026-12-31",self_deadline:"2026-03-01",cross_deadline:"2026-04-01",org_deadline:"2026-06-01",status:"CLOSED"}
  const body = batchPayload(form)
  assert.equal(body.org_deadline,"2026-06-01"); assert.equal(body.branch_deadline,null); assert.equal(body.status,"CLOSED")
  assert.throws(() => batchPayload({...form,self_deadline:"2026-02-30"}))
  assert.throws(() => batchPayload({...form,stage_codes:"1,6"}))
})
test("日期区间使用 DATE_RANGE，来源和关键词转为数组，阶段留空可清除", () => {
  const payload = nodePayload({code:"T10",name:"培训",value_kind:"DATE_RANGE",extract_keywords:"培训,学时",source_material_codes:"CERT",required_from_stage:"3"})
  assert.deepEqual(payload.extract_keywords,["培训","学时"]); assert.equal(payload.stage_code,null); assert.equal(payload.required_from_stage,3)
  assert.throws(() => nodePayload({...payload,value_kind:"RANGE"}))
})
test("派生节点表达式必须完整且非派生节点清空表达式", () => {
  const base = {code:"D01",name:"期满",value_kind:"DERIVED",derive_expr:'{"base":"T14","offset":{"value":1,"unit":"YEAR"}}'}
  assert.equal(nodePayload(base).derive_expr.offset.value,1)
  assert.throws(() => nodePayload({...base,derive_expr:"{}"}))
  assert.equal(nodePayload({...base,value_kind:"DATE"}).derive_expr,null)
})
test("试运行允许参数级别启停，拒绝重复规则和未知字段", () => {
  assert.equal(trialOverrides('{"time_rules":[{"code":"R-T01","is_active":false}]}').time_rules[0].is_active,false)
  assert.throws(() => trialOverrides('{"check_rules":[{"code":"x","foo":1}]}'))
  assert.throws(() => trialOverrides('{"time_rules":[{"code":"x"},{"code":"x"}]}'))
})
test("配置保存使用真实字段并验证日历日期、整数和概率范围", () => {
  assert.deepEqual(settingsPatch("notification",{deadline_remind_days:"3,1,3",in_app:true}),{in_app:true,deadline_remind_days:[3,1]})
  assert.throws(() => settingsPatch("calendar",{holidays:"2026-02-30"}))
  assert.throws(() => settingsPatch("ai",{temperature:3}))
  assert.throws(() => settingsPatch("worker",{concurrency:1.2}))
  assert.equal(settingsPatch("upload",{max_file_mb:"25"}).max_file_mb,25)
})
