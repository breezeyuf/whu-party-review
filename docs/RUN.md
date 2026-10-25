# 运行与验证

项目入口为仓库根目录。后端需要 Python 3.12+、PostgreSQL 14+；前端构建需要 Node.js 22.12+。仓库未包含 `frontend/dist` 构建产物，首次运行前需先构建前端（见「前端修改后重新构建」），否则后端只能提供 API。

## Windows 首次配置

先启动自己的 PostgreSQL，并创建空数据库 `party_review`（例如使用 pgAdmin，或执行 `createdb -U postgres party_review`）。在仓库根目录运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
```

编辑 `backend/.env`，填写数据库地址、用户名和密码。以包内示例为起点，不要把密码放进日志或截图。`HOST` 默认示例为 `127.0.0.1`。不设置管理员密码时，首次启动打印随机初始密码，首次登录必须修改。

随后双击 `start.cmd`，或运行：

```powershell
.\start.ps1
# 也可明确指定 Python：
.\start.ps1 -Python 'C:\path\to\python.exe'
```

默认访问 http://127.0.0.1:8000 。关闭启动窗口或按 Ctrl+C 停止服务。启动脚本先执行只读依赖与数据库检查，再由应用创建表和默认规则。

## 恢复演示数据（推荐）

`database/party_review_20261017.sql` 是演示库的完整结构与数据，包含 24 份档案、72 个提交包、84 份材料版本、276 条问题，以及演示账号与组织架构。恢复命令：

```powershell
psql -U postgres -d party_review -f database\party_review_20261017.sql
```

恢复后演示账号统一密码 `Demo@2026`。公开备份不再包含管理员原密码哈希：`admin` 在 SQL 导入后处于禁用、待恢复状态。使用默认 `ADMIN_USERNAME=admin` 首次启动后端时，系统会保留该用户的 ID 和关联记录，使用当前 `ADMIN_PASSWORD` 或生成随机密码重新启用账号，同时使旧令牌失效；两种方式均要求首次登录改密。未设置 `ADMIN_PASSWORD` 时，新随机密码只在这次初始化的启动控制台显示，请妥善保存。重复启动不会重置已有密码；自定义管理员用户名时，备份中的 `admin` 保持禁用。

这项清理不删除 Git 历史中的旧哈希。升级启动时若检测到管理员仍使用历史公开备份中的那一个密码哈希，将更换为当前 `ADMIN_PASSWORD` 或随机初始密码、要求改密并使旧令牌失效；其他自定义密码不受影响，原本停用的管理员不会因此被重新启用。随机初始密码仅在执行更换的那次启动控制台显示，请在升级前安排好管理员登录方式。演示备份仅供演示与验收，不用于生产环境。

登录页账号提示默认关闭；仅在演示环境显式设置 `DEMO_LOGIN_HINT=1` 才会展示演示账号及密码。关闭提示不会删除或禁用已经创建的演示账号。

注意：仓库未包含 `backend/storage/materials/` 与 `previews/`（各 508 份、约 3.4G，体积原因未入库），备份中的材料记录不会指向实际文件；如需查看材料，请在恢复后于「系统设置」重新初始化演示数据（材料 PDF 自动生成，约 1 分钟）。

也可以不使用备份：启动后在系统设置里调用演示数据初始化，材料 PDF 会现场生成（约 1 分钟）。

## 前端修改后重新构建

```powershell
cd frontend
npm ci
npm test
npm run build
```

开发模式运行 `npm run dev`。使用 `BACKEND_PORT` 改变 Vite 代理的后端端口。后端运行目录不影响配置解析。

## 后端验证

OCR 为可选运行时，安装、模型自检、离线配置与真实识别验收见 [OCR 部署与验收](OCR部署与验收.md)。

数据库结构升级采用带版本、checksum 与事务锁的迁移，空库自动初始化，完整旧版数据库自动接管；重复启动不会重放建表脚本。旧库接管、版本检查和新增迁移步骤见[数据库迁移说明](数据库迁移说明.md)。升级前备份数据库，不能编辑已经应用的迁移文件。

HTTP 请求在 multipart 解析前按实际接收字节执行总体积上限，默认 `MAX_REQUEST_BODY_MB=512`（含表单开销）；材料文件再按 `upload.max_file_mb` 限制读取，ZIP 按 `upload.max_zip_mb` 分块落盘。若提高业务上传上限，应相应调整请求体总上限和反向代理上限。

客户端 IP 默认使用直连来源，忽略 `X-Forwarded-For`。仅在确实使用反向代理时，将该代理的地址/CIDR 填入 `TRUSTED_PROXY_CIDRS`，例如 `127.0.0.1/32,::1/128`；代理必须覆盖传入转发头或追加它实际看到的来源。不要配置不受控网段。自带启动器已关闭 Uvicorn 的隐式代理头处理；若手动启动 Uvicorn，请使用 `python -m uvicorn main:app --no-proxy-headers`，避免在应用校验前改写来源。

服务响应带 `X-Request-ID`；未处理异常返回相同诊断编号。运行日志记录错误类型、调用位置和请求/任务编号，不记录请求正文、密钥、模型提示词或异常原始值。桌面模式沿用 `data/desktop.log`，命令行服务输出到标准日志。

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

新增 PostgreSQL 回归用例默认跳过，必须明确提供测试连接：

```powershell
$env:TEST_DATABASE_URL='postgresql+psycopg://postgres:PASSWORD@127.0.0.1:5432/party_review_test'
..\.venv\Scripts\python.exe -m pytest -q
```

这组用例创建随机 `review_test_*` schema，结束后仅移除该临时 schema，不会隐式使用应用数据库。连接用户需要 CREATE SCHEMA 权限。API 冒烟使用 `DATABASE_URL`，其生命周期会初始化应用结构，因此应指向测试库。

### 没有本机 PostgreSQL 时：临时库跑数据库回归

`pgserver` 自带 PostgreSQL 16.2 二进制，不需要单独安装数据库。它目前没有 Python 3.13 的轮子，
用一份 3.12 环境单独装它即可（后端仍跑在项目自己的 3.13 环境）：

```powershell
uv python install 3.12
uv venv --python 3.12 _pgtools/.venv
uv pip install --python _pgtools/.venv/Scripts/python.exe pgserver
_pgtools\.venv\Scripts\python.exe _tools\pg_run.py _tmp\pgdata   # 打印并常驻一个临时实例
```

拿到连接串后，把 `TEST_DATABASE_URL` 指向该实例的 `postgres` 库、`DATABASE_URL` 指向同实例的
应用库（用于 API 冒烟），即可跑全量回归：

```powershell
$env:TEST_DATABASE_URL='postgresql+psycopg://postgres:@127.0.0.1:<port>/postgres'
$env:DATABASE_URL='postgresql+psycopg://postgres:@127.0.0.1:<port>/party_review'
$env:APP_SECRET_KEY='test-key-0123456789abcdef'
$env:WORKER_ENABLED='0'
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

数据库用例为每个测试模块新建随机 schema（`pytest_*` / `zipconc_*`），测试在事务里跑完即回滚，
结束后 `DROP SCHEMA`，从不连接应用库；`TEST_DATABASE_URL` 未设置时这些用例跳过，跳过不计为通过。
本轮实测：278 passed / 0 skipped。


请求竞态测试：先在前端运行 `npm run dev`，浏览器访问 http://127.0.0.1:5173/tests/hooks.html ，页面显示 4 项实际 React Hook 测试结果。

完整 HTTP 回归脚本为 `backend/tests/e2e_review_flow.py`。它会创建演示数据与合成档案，必须连接独立空测试库，并显式传入 `--allow-test-writes`：

```powershell
$env:TEST_ADMIN_PASSWORD='测试服务初始化时配置的管理员密码'
..\.venv\Scripts\python.exe tests/e2e_review_flow.py --base-url http://127.0.0.1:8001 --allow-test-writes --output e2e-result.json
```

本轮实测环境为 Python 3.13.12、PostgreSQL 16.15、Node.js 24；`backend/requirements-lock.windows-py312.txt` 为上一轮 Windows / Python 3.12 的锁定版本，用于复现。

## 数据与可选能力

`database/` 提供演示数据；`backend/storage/` 未随仓库提供（见上），应用启动时会自动重建空目录，届时在系统设置中初始化演示数据或重新上传材料即可。

大模型默认关闭。需要在系统设置中配置接口和密钥后再验证语义检查；可用「测试连接」确认端点。PaddleOCR 属于可选组件，包内基础依赖不会自动安装或下载模型；未安装时扫描件会提示人工核对。论文、截图与历史报告中的验证数字属各轮原始记录，本轮结果以 `docs/DESIGN.md` 与 `screenshots/` 为准。
