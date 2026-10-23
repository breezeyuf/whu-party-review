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

恢复后演示账号统一密码 `Demo@2026`；管理员 `admin` 的密码为初始化该库时设置的值。注意：仓库未包含 `backend/storage/materials/` 与 `previews/`（各 508 份、约 3.4G，体积原因未入库），备份中的材料记录不会指向实际文件；如需查看材料，请在恢复后于「系统设置」重新初始化演示数据（材料 PDF 自动生成，约 1 分钟）。

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
