# ZIP 材料完整性

分支 `fix/zip-material-integrity` 独立基于 `dev`。不同学生目录中的同名材料现在分别使用独立临时文件保存，保留原始 ZIP 路径用于归属识别，避免后一份覆盖前一份。重试也不会覆盖前次解压结果。

同时按真实路径范围校验存储位置，拒绝落入同名前缀的相邻目录。ZIP 中的绝对路径、目录穿越和符号链接条目不解压；文件数与体积限制继续生效，读取时也核对实际累计体积。损坏 ZIP 仅清理本次创建的文件，保留已有文件。

新增 9 项真实 ZIP 文件测试，覆盖同名材料、重试、路径范围、非法路径、符号链接、目录计数、文件数和体积限制，以及 CRC 错误清理。新增与相关原有测试共 24 项通过。

```powershell
.\.venv\Scripts\python.exe -m pytest -c backend/pytest.ini backend/tests/test_zip_storage.py backend/tests/test_dates.py backend/tests/test_dsl.py backend/tests/test_checks.py backend/tests/test_workflow.py backend/tests/test_app_import.py -q
```

本轮未执行数据库批量归属接口集成或服务器部署验收。
