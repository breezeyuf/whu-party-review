# 统一认证、浏览器会话与模型网络限制

本轮在独立分支整合 PR #38 和 #39，再补齐原设计的三项实现缺口。合并发布前不能把该分支的行为算作主线已上线。

## 登录与升级

默认 `auth.mode=demo`，保留本地账号密码登录；认证设置仅系统管理员可改。`sso` 模式登录页仅显示学校入口，本地登录、改密、重置密码、演示账号生成和旧批量密码文件下载均关闭。SSO 的新用户、导入用户和建档用户只写不可登录标记，不生成第二套密码。既有演示密码哈希保留用于回退，在 SSO 模式不能登录，不自动删除旧数据。

所有浏览器登录使用随机服务端会话。数据库仅存 SHA-256 哈希及过期时间、用户版本和登录模式；浏览器使用 HttpOnly、SameSite=Lax Cookie。服务器模式必须 HTTPS，Cookie 自动带 Secure、`__Host-` 前缀及 `/` 路径，不带 Domain，防止兄弟子域注入同名登录 Cookie；本机 HTTP 演示使用 `/api` 路径。升级后旧 JWT 不再受理，所有用户需重新登录；前端主动清理旧 localStorage 令牌，只保留所选角色。已有脚本需改用 Cookie jar，写请求添加 `X-Requested-With: party-review`；没有刷新令牌接口。

默认会话有效 120 分钟，可通过登录安全设置调整为 1–1440 分钟。到期重新登录。退出删除服务端会话；账号停用、密码或 token_version 改变使原会话失效。变更认证配置撤销现有会话和未完成的 CAS 登录。密码页面及重置按钮在 SSO 模式隐藏。

写请求同时检查非简单请求头、Origin 和 Sec-Fetch-Site；生产只接受 PUBLIC_BASE_URL 同源请求。Cookie 的 HttpOnly 并不能独立解决跨站请求问题，因此这些校验不能删除。开发环境只放行明确配置的前端源。

## CAS 接入

1. 配置 HTTPS `PUBLIC_BASE_URL`，如 `https://review.school.example`，不带路径和查询参数。
2. 学校提供 CAS 登录和 `/serviceValidate` 或 `/p3/serviceValidate` 的 HTTPS 地址，两者须同源。登记的服务需允许 `https://review.school.example/api/auth/sso/callback?state=...`；state 每次随机变化，CAS 登录与验票发送完全一致的 service 值。
3. 预先在本系统开通账号和角色，username 与 CAS 返回的学号/工号完全匹配；不从票据或扩展属性自动授予权限。先确认至少一个已授权管理员能通过学校认证。
4. 系统设置“登录方式”保存 `mode=sso`、`login_url`、`validate_url`。保存后当前登录失效。也可在已升级数据库上使用下面的运维命令。

```powershell
# 使用部署时的 DATABASE_URL、PUBLIC_BASE_URL，勿将真实凭据写入 Git。
python backend/auth_setup.py --mode sso --login-url https://cas.school.example/login --validate-url https://cas.school.example/serviceValidate
# 上一条仅校验；确认学校服务登记和管理员身份后保存：
python backend/auth_setup.py --mode sso --login-url https://cas.school.example/login --validate-url https://cas.school.example/serviceValidate --apply
```

回调使用浏览器绑定、10 分钟有效、数据库原子消费的一次性 state。票据仅用于该次 HTTPS 验票，不入库；不接受代理票据、未知账号或无角色账号。验票不跟随重定向、不使用环境代理，限制响应体大小并拒绝 DTD/实体。应用日志不记录 ticket；反向代理若启用访问日志，也必须省略查询参数。自带 Caddy 配置默认未启用访问日志。

学校认证不可用时，在可信服务器终端使用显式 DATABASE_URL 执行 `python backend/auth_setup.py --mode demo --apply` 回退。已有本地管理员密码可恢复使用；SSO_ONLY 新用户没有本地密码，需要管理员按演示模式重置。此命令不开放为匿名 HTTP 接口，也不会自行修改真实服务器。

## 模型网络策略

文本模型和视觉 OCR 共用限制：保存设置和实际发送请求都校验目标，只允许 RFC1918、IPv6 ULA 和本机回环地址。公网、链路本地、云元数据地址、含凭据/查询/片段的 URL、混合公网/私网 DNS 结果全部拒绝。校园使用公网 IP 的模型也会被拒绝，需要学校提供私网入口，本轮没有添加公网豁免。

请求连接固定到已检查的 IP，保留原始 Host、TLS SNI 及证书校验，避免二次 DNS 解析绕过限制；关闭环境代理和重定向。旧设置中的公网地址不自动迁移，实际调用会明确失败，不能因以前保存过就绕过检查。已有密钥绑定和调用脱敏仍然生效；视觉原图发送继续要求管理员显式开启。

## 验收边界

隔离数据库、模拟 CAS 服务和模拟模型可验证协议、权限、会话失效及网络限制；不能代替学校真实服务登记、真实账号联调、目标服务器和材料准确率验收。Windows 新包的构建/自检也不能代替另一台干净机器和原生 Office 验收。部署前备份数据库，先停止旧 worker，再启动升级版本执行 0005、0006 等待执行的事务迁移。

CAS 协议依据：[Apereo CAS Protocol Specification](https://apereo.github.io/cas/development/protocol/CAS-Protocol-Specification.html)。
