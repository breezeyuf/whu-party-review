# DOCX 完整预览

分支 `fix/docx-preview-pagination` 独立基于 `dev`。移除 DOCX 预览的前 80 段截断和单页压缩，保持 11pt 正文自动分页，并返回真实页数、页面尺寸与文字坐标。表格与段落按原文顺序读取；转换失败会交给解析任务报告，不再写入伪造的 PDF 文件。

预览仍是文本重排结果，并非 Word 原版式的精确复刻。

新增 3 项测试，实际生成含 125 段正文的 DOCX 并读取生成的 PDF，验证末尾内容、页数、坐标、字号、末页渲染、表格顺序和失败处理。新增与相关原有测试共 18 项通过。运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -c backend/pytest.ini backend/tests/test_docx_preview.py backend/tests/test_dates.py backend/tests/test_dsl.py backend/tests/test_checks.py backend/tests/test_workflow.py backend/tests/test_app_import.py -q
```

本轮未执行数据库接口集成或服务器部署验收。
