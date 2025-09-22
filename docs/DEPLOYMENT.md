# tg-sms 部署与运维手册

## 1. 项目概览
- 组件：`bot/` Telegram 机器人、`admin/` FastAPI 后台、`shared/` 公共模块、`frontend/` 预留前端。
- 数据：默认使用 `data/tg_sms.db` (SQLite)，日志目录由 `.env` 中的 `LOG_DIR` 控制。
- 阶段：当前为 50% 骨架，尚需接入真实业务逻辑与前端界面。

## 2. 服务器前置条件
- 操作系统：Ubuntu 20.04+/Debian 11+。
- 系统工具：`python3`、`python3-venv`、`python3-pip`、`sqlite3`、`zip`、`unzip`。`scripts/bootstrap.sh` 会自动使用 `apt-get` 安装（可通过 `SKIP_APT_UPDATE=1` 跳过 `apt update`）。
- 网络要求：可访问 Telegram 及短信平台 API；若有防火墙需提前放行或设置代理。

## 3. 一键安装脚本
```bash
cd /opt/tg-sms-suite        # 替换为实际目录
bash scripts/bootstrap.sh
```
脚本动作：
1. 安装系统依赖并创建虚拟环境（默认 `.venv/`）。
2. 安装 `requirements.txt` 中的 Python 依赖。
3. 若无 `.env`，自动从 `.env.example` 拷贝；首次运行后请填写真实配置。
4. 初始化数据库 `data/tg_sms.db`（仅首次）并创建日志目录。

常用覆盖变量：
- `PYTHON_BIN=/usr/bin/python3.11` 指定解释器。
- `VENV_DIR=/srv/tg-sms-venv` 使用外部虚拟环境。
- `DB_PATH=/var/lib/tg-sms/tg_sms.db` 自定义数据库位置。

## 4. 配置文件说明（`.env`）
- `TELEGRAM_BOT_TOKEN`：Telegram BotFather 分配的 token。
- `SMS_TOKEN`：短信平台（https://sms-szfang.com/yhapi）提供的 API token。
- `BASE_URL`：短信平台请求域名，默认保持示例即可。
- `DB_URL`：后端数据库连接串，默认 `sqlite:///./data/tg_sms.db`，生产可换为 PostgreSQL。
- `JWT_SECRET`：后台登录 JWT 密钥（务必改为随机长串）。
- `POLL_*`：机器人取号轮询节奏参数。
- `PRICE_CURRENCY`：计价货币代码。
- `LOG_DIR`：日志目录，默认 `/var/log/tg-sms-suite`。

## 5. 启动与运行
### 5.1 脚本方式
```bash
bash scripts/run_bot.sh              # 启动 Telegram Bot
HOST=0.0.0.0 PORT=8080 bash scripts/run_admin.sh   # 启动后台 API
```
- `scripts/run_bot.sh` 会自动激活虚拟环境并运行 `python -m bot.app`。
- `scripts/run_admin.sh` 默认使用 `uvicorn`，可通过环境变量调整 `HOST`、`PORT`、`WORKERS`。

### 5.2 Makefile 命令
```bash
make bootstrap    # 等价于 bash scripts/bootstrap.sh
make bot          # 启动机器人
make admin        # 启动后台
make package      # 生成 tg-sms.zip，可通过 ARCHIVE=release.zip 覆盖
make test         # 运行 pytest（待补充实际用例）
```

## 6. systemd 集成
- 样例文件：`docs/systemd/tg-sms-bot.service`、`docs/systemd/tg-sms-admin.service`。
- 使用步骤：
  1. 创建运行用户，例如 `sudo useradd --system --home /opt/tg-sms-suite --shell /usr/sbin/nologin tgsms`。
  2. 将工程解压至 `/opt/tg-sms-suite` 并调整权限：`sudo chown -R tgsms:tgsms /opt/tg-sms-suite`。
  3. 复制服务文件：`sudo cp docs/systemd/*.service /etc/systemd/system/`，按需修改 `WorkingDirectory`、`User`、端口等。
  4. 重载并启用：`sudo systemctl daemon-reload && sudo systemctl enable --now tg-sms-bot tg-sms-admin`。
- 服务日志默认写入 `LOG_DIR`，可配合 logrotate 使用。

## 7. logrotate 配置
- 样例文件：`docs/logrotate/tg-sms-suite`，默认对 `/var/log/tg-sms-suite/*.log` 做每日轮转保留 7 份。
- 部署方法：`sudo cp docs/logrotate/tg-sms-suite /etc/logrotate.d/`，根据实际路径调整。

## 8. 日常运维
- **日志查看**：`tail -f /var/log/tg-sms-suite/*.log`。
- **数据库备份**：`sqlite3 data/tg_sms.db ".backup 'backup/tg_sms_$(date +%F).db'"`（生产环境建议换用远程数据库备份策略）。
- **依赖升级**：更新 `requirements.txt` 后再次执行 `make bootstrap`，脚本会在现有虚拟环境内升级依赖。
- **测试执行**：待补充 `pytest` 用例后运行 `make test`。

## 9. 打包交付
```bash
make package               # 输出 tg-sms.zip
make package ARCHIVE=release-$(date +%F).zip
```
- 打包脚本会自动安装 `zip`（如缺失）并排除 `.venv/`、日志与缓存文件。
- 新服务器解压后再次执行 `make bootstrap` 或 `bash scripts/bootstrap.sh` 即可复现环境。

## 10. 后续待办
- 接入真实数据库模型与业务逻辑，替换模拟数据。
- 实现短信取号/收码/释放/加黑完整流程及错误处理。
- 构建前端界面、权限体系与资金结算流程。
- 补充自动化测试、CI/CD 流水线与安全加固文档。
