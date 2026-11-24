import { test } from "node:test"
import assert from "node:assert/strict"
import { displaySeverities, severityCode, reviewMessage } from "../src/utils/reviewTerms.js"

test("旧等级名称只在显示层映射，内部BLOCK及原对象保持",()=>{
 const rows=[{code:"BLOCK",name:"阻断"},{code:"WARN",name:"警告"}]
 assert.equal(displaySeverities(rows)[0].name,"关键问题")
 assert.equal(rows[0].name,"阻断")
 assert.equal(severityCode("阻断"),"BLOCK");assert.equal(severityCode("关键问题"),"BLOCK")
 assert.equal(reviewMessage("仍有未处理的阻断问题"),"仍有未处理的关键问题")
 assert.equal(reviewMessage("其他历史正文"),"其他历史正文")
})
