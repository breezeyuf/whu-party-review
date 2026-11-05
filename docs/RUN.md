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

## RapidOCR 扫描件识别

本地 OCR 统一使用 RapidOCR + ONNX Runtime；不需要安装 PaddleOCR 或卸载 `opencv-python-headless`。安装基础依赖后，使用官方 PyPI 源安装 OCR，避免镜像尚未同步包时出现 `No matching distribution`：

```powershell
.\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple -r backend/requirements-ocr.txt
.\.venv\Scripts\python.exe backend/ocr_check.py --engine rapidocr --dpi 200
```

命令与“系统设置 → OCR → 测试 OCR”共用真实推理自检：加载模型，识别内置虚构中文日期图片并验证日期可提取。`ok=true` 且退出码 0 才表示本次识别通过；包已安装只表示依赖可发现。自检不使用用户材料。

配置 `auto` 在已安装时使用 RapidOCR，未安装时生成预览并提示人工核对；`rapidocr` 表示显式启用，缺少依赖、模型故障或超时会标记解析失败并提供重试；`none` 关闭识别。旧配置中的 `paddleocr` 在读取时转为 `rapidocr`，新设置不再接受该引擎。失败重试保留已有解析和人工校正。

Windows 打包必须先安装 OCR 依赖；更新后的桌面锁定文件已包含实测版本：

```powershell
.\.venv-desktop\Scripts\python.exe -m pip install --index-url https://pypi.org/simple -r desktop/requirements-lock.windows-py313.txt
.\.venv-desktop\Scripts\python.exe backend/ocr_check.py
.\.venv-desktop\Scripts\python.exe -m desktop.build --output desktop/build/dist-new
```

默认 ONNX 模型随 RapidOCR 包收集进桌面程序。离线部署前在构建环境完成自检，检查模型及运行库齐全。具体范围见 [OCR 部署与验收](OCR部署与验收.md)。更新源码不会自动替换已有 EXE。

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
npm run test:ui
npm run build
```

`npm run build` 会带 manifest 构建，并按 `frontend/bundle-budget.json` 检查每个页面的 gzip 体积与两条验收目标（`/login` ≤125 KiB、`/stats/overview` ≤150 KiB）；未登记预算的页面或超出预算都会失败。查看完整报告用 `npm run bundle:report`，确实需要变大时先说明原因，再执行 `npm run bundle:budget` 刷新预算，让体积变化出现在 diff 里。CI 的前端任务执行同一条 `npm run build`。

开发模式运行 `npm run dev`。使用 `BACKEND_PORT` 改变 Vite 代理的后端端口。后端运行目录不影响配置解析。

## 后端验证

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
_pgtools\.venv\Scripts\python.exe tools\pg_run.py _tmp\pgdata   # 打印并常驻一个临时实例
```

连接串同时写入 `_tmp\pg_uri.txt`，方便另开终端取用。

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
本地实测（2026-10-28，PostgreSQL 16.15）：`TEST_DATABASE_URL` 与 `DATABASE_URL` 同时指向测试库时
**719 passed / 0 skipped**；只设 `TEST_DATABASE_URL` 时两条 API 冒烟用例因缺少 `DATABASE_URL` 跳过
（717 passed / 2 skipped）。CI 两个变量都配置，并断言零跳过。

### 工具脚本

`tools/` 是本地复现后端验收的脚本，不参与应用运行：

| 脚本 | 用途 |
| --- | --- |
| `run_db_tests.py` | 起临时 PostgreSQL 跑后端全量 pytest，结束后停库并删除数据目录；`TEST_DATABASE_URL` 已存在时改为复用外部实例 |
| `pg_run.py` | 常驻一个临时 PostgreSQL 实例，并把连接串写入 `_tmp/pg_uri.txt` 供手工联调 |

前端体积核对脚本在 `frontend/scripts/bundle-budget.mjs`，通过 `npm run build`（检查）、`npm run bundle:report`（报告）、
`npm run bundle:budget`（刷新预算）使用，详见上一节。

应用启动只执行 `backend/migrations/` 下带版本与校验和的迁移，不再重放 `backend/schema.sql`。结构核对以
`pytest backend/tests/test_migrations.py` 为准：空库初始化、重复启动不重放 DDL、旧库接管、校验和不符与
并发启动都有用例；`backend/tests/test_review_regressions.py` 另外验证旧结构上的兼容路径。


请求竞态测试：先在前端运行 `npm run dev`，浏览器访问 http://127.0.0.1:5173/tests/hooks.html ，页面显示 4 项实际 React Hook 测试结果。

完整 HTTP 回归脚本为 `backend/tests/e2e_review_flow.py`。它会创建演示数据与合成档案，必须连接独立空测试库，并显式传入 `--allow-test-writes`：

```powershell
$env:TEST_ADMIN_PASSWORD='测试服务初始化时配置的管理员密码'
..\.venv\Scripts\python.exe tests/e2e_review_flow.py --base-url http://127.0.0.1:8001 --allow-test-writes --output e2e-result.json
```

本轮实测环境为 Python 3.13.12、PostgreSQL 16.15、Node.js 24；`backend/requirements-lock.windows-py312.txt` 为上一轮 Windows / Python 3.12 的锁定版本，用于复现。

## 数据与可选能力

`database/` 提供演示数据；`backend/storage/` 未随仓库提供（见上），应用启动时会自动重建空目录，届时在系统设置中初始化演示数据或重新上传材料即可。

大模型默认关闭。需要在系统设置中配置接口和密钥后再验证语义检查；可用「测试连接」确认端点。源码环境的 RapidOCR 依赖单独安装，默认 auto 模式未安装时扫描件保留预览并提示人工核对。论文、截图与历史报告中的验证数字属各轮原始记录，当前实现与本轮验证见各项修复记录。
# 认证升级说明

生产统一认证、Cookie 会话、旧客户端升级和校内模型限制见 [统一认证与模型网络策略](production-auth-and-model-policy.md)。升级后旧 JWT 失效，需要重新登录；配置 SSO 前先完成学校服务登记和管理员身份核对。
