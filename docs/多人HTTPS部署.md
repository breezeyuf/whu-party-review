# 多电脑 HTTPS 部署

当前桌面 EXE 仍只用于单机。本目录中的 `server/` 提供一台 Linux 服务器上的 PostgreSQL、应用和 Caddy 反向代理组合：其他电脑用同一 HTTPS 地址访问，业务数据和文件集中保存。邮件、短信仍仅配置，不发送。

## 正式部署

1. 准备能运行 Docker Compose 的 Linux 主机、指向该主机的域名，并开放入站 TCP 80/443。安装 Docker Engine 与 Compose 插件。确认 `172.30.217.0/24` 未与主机或现有容器网络冲突；如冲突，连同 `TRUSTED_PROXY_CIDRS` 和代理静态地址一起更换。
2. 在 `server/` 将 `.env.server.example` 复制为 `.env.server`，填写域名、`PUBLIC_BASE_URL`、独立随机的 `POSTGRES_PASSWORD`、`APP_SECRET_KEY` 和管理员初始密码。`DATABASE_URL` 中的密码必须与数据库密码相同，并按 URL 规则编码。该文件不能提交到 Git；首次启动前限制只有部署管理员可读。
3. 在 `server/` 执行 `docker compose --env-file .env.server config --quiet`，再执行 `docker compose --env-file .env.server up --build -d`。确认 `docker compose --env-file .env.server ps` 中三个服务健康。
4. 在另一台电脑打开 `https://<域名>/api/health`，确认 `data.db` 为 `ok`；再打开首页完成管理员首次登录、改密。用两台电脑的不同账号检查权限、上传材料、刷新列表和退出登录。Caddy 自动申请并续期公开域名证书，也将 HTTP 重定向至 HTTPS。[Caddy 自动 HTTPS](https://caddyserver.com/docs/automatic-https)

代理只公布 80/443；应用和数据库没有宿主机端口。应用只信任本组合里 Caddy 的固定代理地址，以记录真实访问 IP；Caddy 覆盖客户端传入的 `X-Forwarded-For`。服务器模式要求 HTTPS 公共地址、持久化材料目录、独立凭据，并拒绝演示登录提示、默认数据库密码和跨域开放。配置检查失败时应用拒绝启动。

## 本地 HTTPS 验证

安装 Docker 的电脑可以在 `server/.env.server` 设 `PARTY_REVIEW_DOMAIN=localhost`、`PUBLIC_BASE_URL=https://localhost:8443`、`HTTP_PORT=8080`、`HTTPS_PORT=8443`、`CADDY_CONFIG=Caddyfile.local`，其他密码换成独立随机值。启动组合后执行：

```sh
docker compose --env-file .env.server cp proxy:/data/caddy/pki/authorities/local/root.crt ./local-root.crt
curl --cacert ./local-root.crt https://localhost:8443/api/health
```

仅为本地测试导入该根证书；正式域名使用公开可信证书，不使用 `tls internal`。仓库自动回归还会启动一次临时 HTTPS 服务，以真实 TLS 握手验证健康接口、错误密码登录与跨域限制。该回归不替代在目标主机运行上述 Caddy/Compose 检查。

## 数据与恢复

备份必须同时包含数据库、`storage` 卷和稳定的 `APP_SECRET_KEY`；Caddy 的 `caddy_data` 卷保存证书状态。可在维护窗口运行 `docker compose --env-file .env.server exec -T db pg_dump -U party_review -Fc party_review > party-review.dump`，并另行备份 `storage` 卷与私密配置。仅保存数据库会丢材料；更换应用密钥会使既有加密字段与令牌不可用。恢复时先停应用，恢复数据库与材料卷，再用原密钥启动并检查健康、历史材料下载和账号权限。不要把备份或配置放入公开代码库。

此交付没有目标服务器、域名或真实证书，因此没有对公网部署。首次正式上线还需在该主机完成 Compose 运行、证书、跨电脑权限和备份恢复验收。
