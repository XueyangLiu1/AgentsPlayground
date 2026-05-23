# 家庭信用卡福利追踪 Dashboard — MVP 任务规格

## 背景

陛下和皇后都有多张 Chase / Amex 信用卡，需要追踪：
- 各种年度/季度/月度福利（Uber Cash、酒店报销等）的领取进度
- 开卡奖励（Sign-up Bonus）的消费达标进度
- 年费到期时间，决定续 / 降级 / 关卡
- 持卡满 1 年才能关卡的时间限制

目标：一个本地部署、家庭内网访问的 Dashboard，先做信用卡福利追踪模块。

## 范围与原则

- **MVP 优先**：跑通核心闭环，先粗后精
- **可迭代可扩展**：后续会加更多模块（家庭日历、订阅、保修等）
- **本地部署**：Mac Mini 上 docker-compose，数据全在本地
- **无账号机制**：家庭内网，按持卡人切 tab 即可
- **手动录入**：暂不接 Plaid，全部手动打勾

## 技术栈

| 层 | 选型 | 备注 |
|----|------|------|
| 后端 | FastAPI + SQLAlchemy 2.x + Pydantic v2 | Python 3.11+ |
| 数据库 | SQLite | 文件持久化到 `./data/db.sqlite` |
| 前端 | Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui | Node 20+ |
| 反代 | Caddy | 监听 80，反代前端 + `/api` 到后端 |
| 容器编排 | docker-compose | 一键启动 |

## 数据模型

所有表统一加 `created_at` / `updated_at`（自动维护）。

### Cardholder（持卡人）
- `id` int PK
- `name` str unique (如 "Shawn", "Empress")
- `color_tag` str (HEX color, 用于 UI tab 标记)

### Card（信用卡）
- `id` int PK
- `cardholder_id` FK → Cardholder
- `issuer` enum: `Chase` | `Amex` | `Other`
- `name` str (如 "Amex Platinum")
- `opened_date` date
- `annual_fee` float (单位 USD)
- `fee_waived_first_year` bool
- `status` enum: `active` | `pending_downgrade` | `pending_close` | `closed`
- `next_fee_date` date (下次年费日期)
- `can_close_after_date` date (可关卡日期，通常开卡日 + 365)
- `notes` text nullable

### Benefit（福利项模板）
- `id` int PK
- `card_id` FK → Card
- `name` str (如 "Uber Cash")
- `amount` float (USD)
- `frequency` enum: `monthly` | `quarterly` | `yearly`
- `cycle_type` enum: `calendar_year` | `anniversary_year` | `statement_month`
- `category` enum: `credit` | `lounge` | `points` | `experience`
- `notes` text nullable

### BenefitProgress（福利领取记录）
- `id` int PK
- `benefit_id` FK → Benefit
- `period` str (如 "2026-Q1"、"2026-06"、"2026"，依 frequency 决定格式)
- `claimed_amount` float
- `claimed_date` date
- `claimed_by` str (可填持卡人名字，但允许自由文本)
- `notes` text nullable

### SignUpBonus（开卡奖励）
- `id` int PK
- `card_id` FK → Card
- `required_spend` float
- `deadline_date` date
- `reward_description` str (如 "80,000 MR points")
- `current_spend` float (默认 0)
- `completed` bool (默认 false)

### Reminder（自定义提醒）
- `id` int PK
- `card_id` FK → Card nullable
- `title` str
- `due_date` date
- `status` enum: `pending` | `done` | `dismissed`
- `recurring` enum: `none` | `yearly` | `monthly` (默认 `none`)

## 后端 API

每个实体一套标准 CRUD：
- `GET /api/{entity}` 列表（支持 query filter，如 `?cardholder_id=1`）
- `GET /api/{entity}/{id}` 详情
- `POST /api/{entity}` 创建
- `PATCH /api/{entity}/{id}` 更新
- `DELETE /api/{entity}/{id}` 删除

实体路径：
- `/api/cardholders`
- `/api/cards`
- `/api/benefits`
- `/api/benefit-progress`
- `/api/sign-up-bonuses`
- `/api/reminders`

### 专用端点

- `GET /api/dashboard/overview`
  返回：
  - `unclaimed_this_period`: 本期（当月/季/年依 frequency）尚未打勾的福利列表
  - `sub_gaps`: 未完成的 SUB 列表 + 剩余消费 + 剩余天数
  - `fee_due_soon`: 30 天内年费到期的卡列表
  - `closable_soon`: 30 天内 `can_close_after_date` 到期的卡列表
  - `family_summary`: 本月家庭已领取金额 / 本月家庭可领取总金额

- `POST /api/benefits/{id}/claim`
  Body: `{ claimed_amount?: float, claimed_date?: date, claimed_by?: str, notes?: str }`
  自动根据 benefit.frequency 计算当前 period，创建 BenefitProgress 记录。

- `GET /api/cardholders/{id}/cards`
  返回该持卡人的所有卡片，附带每张卡的本期福利进度摘要。

### Pydantic schema 规范

每个实体三套 schema：`{Entity}Base`、`{Entity}Create`、`{Entity}Read`。`Read` 含 id + 时间戳。

## 卡片预设（presets.py）

内置以下卡片模板（持卡人空着，由用户选择）。每个模板包含默认 `annual_fee` 和典型 `benefits` 列表（金额、frequency、cycle_type、category）。

**Chase:**
- Sapphire Reserve
- Sapphire Preferred
- Freedom Unlimited
- Ink Business Preferred

**Amex:**
- Platinum
- Gold
- Green
- Blue Cash Preferred

数据按你的常识填即可，金额/福利不全也没关系，标 TODO 注释，后续陛下会更新。

API：`GET /api/presets/cards` 返回预设列表。前端 `/new` 页面用下拉选择，选中后自动填表单。

## 前端页面

### 路由

- `/` — 总览 Dashboard
- `/holder/[id]` — 持卡人 tab（含 `/holder/all` 表示全家视图）
- `/card/[id]` — 卡片详情
- `/new` — 录入页（持卡人、卡片、福利、SUB、提醒五种实体的录入入口）

### `/` 总览

- **本月待薅福利**（按金额降序）— 每行：卡名 + 福利名 + 金额 + 持卡人 tag + 一键打勾按钮
- **SUB 缺口** — 卡名 + 剩余消费 + 剩余天数（红色高亮 < 30 天）
- **年费提醒** — 30 天内 `next_fee_date` 到期的卡
- **可关卡提醒** — 30 天内 `can_close_after_date` 到期的卡
- **家庭本月统计** — 已领取 $X / 可领取 $Y

### `/holder/[id]`

- 顶部 tab 切换：Shawn / Empress / 全家
- 卡片网格（每张卡一个 Card 组件）
- 每张卡显示：卡名、年费、状态徽章、本期福利进度条（已领 / 总值）

### `/card/[id]`

- 头部：卡名、持卡人、状态、年费、可关卡日期
- Tab 1: 福利列表（每个福利一行带打勾按钮 + 历史记录）
- Tab 2: SUB 进度（进度条 + 编辑当前消费）
- Tab 3: 提醒
- 编辑/删除/改状态按钮

### `/new`

- 顶部选择"录入类型"
- 选"卡片"时，先选预设（下拉），加载默认值，再选持卡人、填日期，提交时一并创建卡 + 默认福利
- 其他类型常规表单

### UI 要求

- 响应式（桌面 + 移动端 Safari/Chrome）
- shadcn/ui 默认主题，简洁干净
- 移动端能加到 iOS 主屏（基础 PWA manifest + 图标即可，无需 service worker）

## 目录结构

```
family-dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── presets.py
│   │   └── routers/
│   │       ├── cardholders.py
│   │       ├── cards.py
│   │       ├── benefits.py
│   │       ├── benefit_progress.py
│   │       ├── sign_up_bonuses.py
│   │       ├── reminders.py
│   │       ├── dashboard.py
│   │       └── presets.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_*.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── holder/[id]/page.tsx
│   │   ├── card/[id]/page.tsx
│   │   └── new/page.tsx
│   ├── components/
│   ├── lib/
│   │   └── api.ts
│   ├── public/
│   │   └── manifest.json
│   ├── Dockerfile
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
├── caddy/
│   └── Caddyfile
├── data/
│   └── .gitkeep
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Docker / 部署

### docker-compose.yml 要求

- 服务：`backend`、`frontend`、`caddy`
- `backend` 挂载 `./data:/app/data`
- 后端环境变量：`DATABASE_URL=sqlite:////app/data/db.sqlite`
- 前端环境变量：`NEXT_PUBLIC_API_BASE=/api`
- Caddy 监听 80，反代：
  - `/api/*` → `backend:8000`
  - `/*` → `frontend:3000`
- 所有服务 `restart: unless-stopped`
- 后端启动时自动 `Base.metadata.create_all`（MVP 阶段够用，不强制 alembic）

### Caddyfile 样例方向

```
:80 {
  handle_path /api/* {
    reverse_proxy backend:8000
  }
  reverse_proxy frontend:3000
}
```

### 一键启动

```
cd family-dashboard
docker-compose up -d --build
```

访问 `http://localhost`、`http://<mac-mini-ip>` 或 `http://dashboard.local`（mDNS 由系统层处理，文档建议陛下后续配）。

## 测试要求

- 后端：`pytest` 跑通基础 CRUD + dashboard overview + `claim` 端点，至少 10 个测试
- 前端：能 build 通过（`npm run build`）即可，组件单测可选
- 仓库 GitHub Actions 不强制扩展，但 `pytest` 必须本地通过

## 验收标准

1. `cd family-dashboard && docker-compose up -d --build` 一键启动，无报错
2. `http://localhost/` 打开看到总览页
3. 通过 `/new` 录入：持卡人（你 + 皇后）→ 卡（用预设）→ 福利、SUB、提醒
4. 打勾一个福利后，总览页"待薅"列表减少、"家庭本月统计"已领金额增加
5. 编辑卡片状态 → `pending_close` → 卡片详情显示对应徽章
6. 移动端浏览器访问 UI 不破版
7. 重启 `docker-compose down && docker-compose up -d`，数据保留
8. `README.md` 写清启动、停止、备份 SQLite、查日志、重置数据五个命令
9. 后端 `pytest` 全部通过

## 不在本期范围（v2 再说）

- Discord/webhook 推送提醒
- 自动备份脚本（v1.5 加，先在 README 给手动命令）
- 历史净收益图表
- 多人并发编辑冲突处理
- 账号 / 认证
- Plaid 自动交易导入

## 工作流程

- 分支：`feature/family-dashboard`（工部尚书已创建并 push）
- 完成后宇文恺自测 → @ 祖冲之审核
- 祖冲之**必须实际跑 `docker-compose up`，测试 CRUD 流程**，不允许只看代码
- 审核通过后 @ 工部尚书验收
- 工部尚书验收后请陛下决定是否 merge

## 备注

如执行过程中发现 spec 不合理或缺漏，及时提出，工部尚书会与陛下商议后更新本文档。
