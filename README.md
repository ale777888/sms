# tg-sms-suite

> Telegram 接码机器人 + FastAPI 后台（已接入真实短信平台 API）

## 当前能力

- ✅ **短信平台真实对接**：封装 `myInfo/getItem/getPhone/getPhoneCode/setRel/addBlack` 等接口，含错误码处理与重试机制。
- ✅ **Telegram 机器人**：
  - 主菜单展示项目、国家、余额。
  - 支持按项目/国家取号、自动落库及状态管理。
  - 一键收码、释放、加黑，自动记录验证码，并在退出时兜底释放。
- ✅ **数据库持久化**：基于 `SQLAlchemy` + `SQLite`，提供用户、项目、订单模型与仓储方法。
- ✅ **后台接口**：`/api/orders` 返回真实订单列表，`/api/stats/summary` 输出订单统计与收入汇总。
- ✅ **脚本与配置**：提供 `.env.example`、`requirements.txt`、`Makefile`、运维脚本及日志目录初始化。

## 关键技术栈

- **Python 3.11** / `aiogram 3` / `FastAPI` / `SQLAlchemy 2` / `httpx`
- **数据库**：`SQLite`（默认，可通过 `DB_URL` 切换至其他数据库）
- **消息平台**：`https://sms-szfang.com/yhapi`

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 填写 TELEGRAM_BOT_TOKEN / SMS_TOKEN 等
bash scripts/bootstrap.sh
```

运行服务：

```bash
bash scripts/run_bot.sh      # 启动 Telegram Bot
bash scripts/run_admin.sh    # 启动 FastAPI 后台
```

## 目录概览

```
bot/            # Telegram 机器人
admin/          # FastAPI 后台
shared/         # 公共模块（配置、短信客户端、数据库、仓储等）
migrations/     # 初始 SQL 建表脚本
scripts/        # Bootstrap/运行/打包脚本
frontend/       # 预留前端目录（下一阶段接入）
```

## 下一阶段扩展方向

1. **资金与风控**：实现余额冻结、计费、退款、黑名单策略、风控监控等。
2. **前端控制台**：构建 React/TypeScript 后台页面，覆盖仪表盘、订单、项目、充值审核。
3. **自动化测试与 CI/CD**：补充单元/集成测试、流水线、监控告警。
4. **多租户与权限**：完善角色体系、操作审计、敏感操作审批流程。

## 注意事项

- 真实短信平台需严格控制释放/加黑调用，否则可能被封禁账号或扣费。
- `.env` 中的 `SMS_TOKEN/JWT_SECRET` 等需使用生产级随机值，并妥善保密。
- 默认数据库为 `SQLite`，生产环境建议迁移至 `PostgreSQL` 并启用 Alembic 迁移。
