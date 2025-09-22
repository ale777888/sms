# tg-sms-suite

> Telegram 接码机器人 + 后台管理系统（阶段性交付 50%）

## 当前阶段成果（50%）

- ✔️ 完成整体目录结构、公共层（配置、模型、定价、短信客户端）
- ✔️ 提供初版数据库建表脚本 `migrations/versions/0001_init.sql`
- ✔️ Telegram Bot 入口、主菜单、基础 Handler 与键盘布局已搭建（含占位逻辑）
- ✔️ FastAPI 后台骨架、JWT 登录、基础统计/订单接口占位、认证依赖完成
- ✔️ `.env.example`、`requirements.txt`、前端目录、脚本目录等准备就绪
- ⚠️ 功能仍使用模拟数据，尚未接入真实业务逻辑/数据库/短信平台

## 下一阶段（剩余 50%）待办

1. **Telegram Bot**
   - 接入数据库与定价引擎，完成国家/项目/取号/收码完整流程
   - 实现订单轮询、释放、加黑逻辑与标准回执模板
   - 编写资金冻结/结算调度、异常处理与统一日志

2. **后台 FastAPI + 前端**
   - 完成实际数据模型、SQLAlchemy ORM、CRUD 接口
   - 实现项目/价格/订单/资金/风控等完整 API
   - 搭建 React 前端（登录、仪表盘、订单、价格配置、充值审核等）

3. **运维与测试**
   - 编写 install/deploy/update/rollback/status 脚本
   - 补充 systemd、logrotate、USDT(TRC20) 充值对接指引
   - 添加单元/集成测试、文档中部署命令清单、架构图

## 快速开始（阶段性）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 根据实际环境填写 .env
sqlite3 data/tg_sms.db < migrations/versions/0001_init.sql
python -m bot.app  # 启动机器人（当前为占位逻辑）
uvicorn admin.main:app --reload  # 启动后台（占位接口）
```

## 目录概览

```
bot/            # Telegram 机器人代码（主菜单与 handlers 已就绪，后续补充业务逻辑）
admin/          # FastAPI 后台骨架（含认证、统计、订单占位）
shared/         # 公共模块：配置、模型、定价引擎、短信客户端
migrations/     # 初始 SQL 脚本（下一阶段接入 Alembic）
frontend/       # 预留 React 前端目录
scripts/        # 运维脚本（下一阶段补充）
```

## 重要说明

- 所有功能仍处于占位阶段，真实逻辑将在后续补充。
- 代码遵循模块化拆分，方便下一阶段接入数据库、任务调度、实际接口。
- 本阶段产物满足“信息架构、骨架、配置、模拟流程”要求，为剩余 50% 实现打好基础。
