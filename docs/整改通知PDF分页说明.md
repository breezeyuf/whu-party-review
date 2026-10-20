# 整改通知 PDF 分页

本次补充 B 负责的通知导出功能，分支为 `fix/notice-pdf-pagination`，独立基于 `dev`。

原有导出将全部问题放进同一页，内容多时会整体缩小。现在按 A4 页面连续排版，正文保持 11pt，页脚显示当前页数和总页数。问题说明、修改建议、缺项清单和审核意见可以跨页续写。

标题和正文中的尖括号、与号等按原文保留，不再被作为 HTML 标签解释；换行保留。下载接口与文件名约定不变，本次未改动 Word 导出、数据库和审核流程。

## 验证结果

新增 5 项自动化测试，覆盖短通知、45 条问题、单条超长问题、60 条缺项、含 HTML 符号的正文。测试实际生成并重新读取 PDF，检查内容完整性、A4 页面、正文字号、边界和页码。

新增测试及相关原有测试共 20 项通过。用于视觉检查的 45 条问题样例生成 3 页，已逐页渲染检查，中文和页码可读。

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -c backend/pytest.ini backend/tests/test_notice_export.py backend/tests/test_dates.py backend/tests/test_dsl.py backend/tests/test_checks.py backend/tests/test_workflow.py backend/tests/test_app_import.py -q
```

本轮未连接数据库进行接口集成测试，也未执行服务器部署验收。
