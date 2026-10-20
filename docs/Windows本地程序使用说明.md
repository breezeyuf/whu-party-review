# Windows 本地程序

本文说明 2026-10-20 交付的本地程序。已完成的成品验证及其范围见 [Windows 本地程序验收](Windows本地程序验收.md)。

将完整 `PartyReview` 文件夹放到全英文路径（例如 `D:\PartyReview`）后，双击 `PartyReview.exe`。程序内置 Python、前端、后端和 PostgreSQL，无需安装 Node.js、Python 或数据库，也无需运行终端命令。适用于 Windows 10/11 64 位；桌面窗口使用系统 WebView2 运行时。

## 第一次打开

1. 双击 `PartyReview.exe`，等待“准备本地数据库”完成。
2. 双击同目录 `FirstLogin.cmd`，查看本机自动生成的管理员初始密码。
3. 在程序中用 `admin` 登录，按提示修改密码，重新登录后选择系统管理员或组织管理员身份。
4. 管理员可以创建组织、学生账号及发展档案。学生、审核员、管理员登录后进入各自工作台。

初始密码每台新工作台随机生成，文件位于 `data/FirstLogin.txt`。修改后旧密码失效。

想先体验流程，可以双击 `StartDemo.cmd`。它首次生成标注为演示的虚构账号、档案和材料，并存入独立的 `demo-data/`。登录页展开演示账号，例如学生 `demo_stu01`、审核员 `demo_branch1`、组织管理员 `demo_org`，密码均为 `Demo@2026`。审核员可能有两个授权身份，先选择本次办理身份。演示模式的初始 admin 密码见 `demo-data/FirstLogin.txt`。

## 本地保存与退出

关闭程序窗口会停止本地后端和本程序的数据库，账号、材料、修改和审核结果仍会保留。首次生成演示材料可能需要约一分钟；后续启动直接读取已有数据。

程序只监听本机 `127.0.0.1`，适合单机使用。其他同学不会自动共享本机数据；多人协作仍需部署团队服务。

空白工作台数据在 `data/`，演示数据在 `demo-data/`，包括数据库、原件、预览、加密密钥和日志。**备份时先退出程序，再复制整个数据文件夹；恢复时保持文件夹完整。不要只备份数据库而遗漏密钥与材料。** 升级程序前先备份，保留这两个数据目录。不要单独移动 exe，`_internal/` 包含所需运行文件。

## 离线能力

本机账号、材料上传、PDF／Word 解析、清单检查、规则自查、整改、审核及记录保存使用本地服务。在线大模型默认关闭，需要自行配置接口并联网。此包不含 PaddleOCR 模型，纯扫描图片按现有实现提示人工核对，不把扫描件识别能力标成已安装。

如果系统没有 WebView2，可从微软官方页面安装后重新打开：https://developer.microsoft.com/microsoft-edge/webview2/ 。本机生成包前已检查 WebView2 存在。

程序首次启动失败时，查看相应数据文件夹里的 `desktop.log` 和 `postgres.log`。连续双击同一个工作台时会提示已运行，请回到已有窗口。

## 从源码重新构建（维护者）

维护者需准备 Windows 64 位、Python 3.13 和 Node.js／npm。在项目根目录创建独立环境，按本次 Windows Python 3.13 的完整锁定版本安装后运行：

```powershell
python -m venv .venv-desktop
.\.venv-desktop\Scripts\python.exe -m pip install -r desktop/requirements-lock.windows-py313.txt
.\.venv-desktop\Scripts\python.exe -m desktop.build
```

首次构建会从 PostgreSQL 官方指定发行商下载 Windows 数据库压缩包、构建前端并打包；下载和安装依赖需要联网。最终目录默认在 `desktop/build/dist/PartyReview/`，不会把测试库、现有用户材料和个人凭证编入程序。锁定文件见 [Windows Python 3.13 依赖版本](../desktop/requirements-lock.windows-py313.txt)，前端依赖使用 `frontend/package-lock.json`。这里的命令用于复现构建，后续代码合并后的检查结果应记录在相应 PR 中。

实现参考：[PyInstaller 打包文档](https://pyinstaller.org/en/stable/spec-files.html)、[pywebview 桌面打包](https://pywebview.flowrl.com/guide/freezing.html)、[PostgreSQL Windows 发行包](https://www.postgresql.org/download/windows/)。
