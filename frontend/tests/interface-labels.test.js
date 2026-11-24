import {test} from "node:test"
import assert from "node:assert/strict"
import {uiLabel,handoverReasonLabel,parsedWarning} from "../src/utils/interfaceLabels.js"

test("known backend enums display Chinese without modifying API values",()=>{
 for (const [code,expected] of [["PENDING","待处理"],["pending","待处理"],["AUTO","自动识别"],["SENT","已发送"],["MANUAL","人工校正"],["RECHECK","整改复核"],["RULE_LLM","规则与大模型检查"],["BRANCH_REVIEWER","党支部审核员"]])assert.equal(uiLabel(code),expected)
 assert.equal(uiLabel("rapidocr"),"RapidOCR")
 assert.equal(uiLabel("自定义的中文说明"),"自定义的中文说明")
 assert.equal(uiLabel(null),"—")
})
test("handover reasons explain manual review without equating the reason with OCR failure",()=>{
 assert.equal(handoverReasonLabel("LOW_CONFIDENCE"),"自动检查结果需进一步核实")
 assert.equal(handoverReasonLabel("KEY_STAGE"),"本阶段须由人工确认")
 assert.equal(handoverReasonLabel("NEEDS_JUDGEMENT"),"内容需要人工判断")
 assert.equal(handoverReasonLabel("MATERIAL_CONFLICT"),"不同材料的时间信息存在冲突")
})
test("image upload not authorized is informational, while genuine warnings remain warnings",()=>{
 const original="视觉 OCR 未发送图片：尚未允许将材料图片发送至配置的服务"
 const result=parsedWarning(original)
 assert.equal(result.informational,true)
 assert.match(result.message,/未授权发送原图/)
 assert.match(result.message,/不表示本地识别失败/)
 assert.equal(parsedWarning({message:"本地识别失败，请重试"}).informational,false)
 assert.equal(parsedWarning({message:"本地识别失败，请重试"}).message,"本地识别失败，请重试")
 assert.equal(original,"视觉 OCR 未发送图片：尚未允许将材料图片发送至配置的服务")
})
