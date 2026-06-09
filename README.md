# AI 智能客服系统

面向企业内部的智能问答系统，支持结构化数据查询、非结构化知识检索、以及混合场景的智能问答。

> **当前阶段**: Phase 1 — 基础框架搭建完成。前后端骨架可启动、数据库可连通、迁移可执行。

---

## 技术栈 (Phase 1)

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (异步) |
| ORM | SQLAlchemy 2.0 (async) |
| 数据库迁移 | Alembic |
| 数据库 | PostgreSQL 16 |
| 前端框架 | Vue 3 (Composition API) + Vite |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| 包管理 | uv (Python) / npm (Node.js) |

---

## 项目结构

```
ai-customer-service/
├── server/                        # 后端
│   ├── app/
│   │   ├── main.py                # FastAPI 入口 + lifespan
│   │   ├── config.py              # Pydantic Settings 配置
│   │   ├── api/
│   │   │   ├── deps.py            # 依赖注入 (get_db)
│   │   │   └── v1/
│   │   │       └── router.py      # v1 路由 (GET /health)
│   │   ├── models/
│   │   │   └── base.py            # SQLAlchemy Base + BaseModel
│   │   ├── middleware/
│   │   │   └── cors.py            # CORS 中间件
│   │   └── utils/
│   │       └── logger.py          # JSON 格式日志
│   ├── alembic/                   # 数据库迁移
│   │   ├── env.py
│   │   └── versions/
│   ├── .env.example               # 环境变量模板
│   └── requirements.txt           # Python 依赖
├── client/                        # 前端
│   └── src/
│       ├── main.js                # Vue 入口 (Element Plus + Router + Pinia)
│       ├── App.vue                # 全局布局 + 导航栏
│       ├── router/index.js        # 路由配置
│       ├── api/index.js           # Axios 封装 + 拦截器
│       └── views/
│           ├── HomeView.vue       # 首页
│           ├── ChatView.vue       # 对话页
│           └── KnowledgeView.vue  # 知识库页
├── deploy/
│   └── docker-compose.yml         # PostgreSQL 16
└── docs/
    ├── DEVELOPMENT.md             # 完整开发文档
    └── PHASE1-SETUP.md            # Phase 1 搭建步骤
```

---

## 快速开始

### 前提条件

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- uv

### 1. 启动 PostgreSQL

```bash
cd deploy
docker compose up -d postgres
```

### 2. 安装后端依赖

```bash
cd server

# 创建虚拟环境
uv venv --python 3.12
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入数据库连接信息（默认值即可运行）
```

`.env` 最小配置：

```env
APP_NAME=
APP_ENV=
APP_DEBUG=
APP_PORT=
DATABASE_URL=
DATABASE_URL_SYNC=
SECRET_KEY=
ACCESS_TOKEN_EXPIRE_MINUTES=
```

### 4. 执行数据库迁移

```bash
cd server
source .venv/bin/activate
alembic upgrade head
```

### 5. 启动后端

```bash
cd server
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger 文档。

### 6. 安装并启动前端

```bash
cd client
npm install
npm run dev
```

访问 http://localhost:5173 查看前端页面。

---

## API 端点 (Phase 1)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 + 数据库连通性 |
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | OpenAPI Schema |

### 健康检查响应

```json
{
    "status": "ok",
    "database": "connected",
    "version": "0.1.0"
}
```

---

## 开发命令

```bash
# ── 后端 ──
cd server && source .venv/bin/activate

uvicorn app.main:app --reload --port 8000    # 启动开发服务器
alembic revision --autogenerate -m "描述"     # 生成迁移
alembic upgrade head                          # 执行迁移
alembic downgrade -1                          # 回滚一步
alembic current                               # 查看当前版本
ruff check .                                  # 代码检查
pytest                                        # 运行测试

# ── 前端 ──
cd client

npm run dev                                   # 启动开发服务器
npm run build                                 # 生产构建
```

---

## 下一步 (Phase 2)

- [ ] 业务模型 (Employee, Project, Attendance)
- [ ] 核心问答接口 (POST /api/v1/qa/ask)
- [ ] SQL 安全生成与执行服务
- [ ] 知识库 BM25 检索服务
- [ ] 意图分类 (structured / knowledge / hybrid)
- [ ] 问答 UI + 来源引用展示

详见 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) 和 [docs/PHASE1-SETUP.md](docs/PHASE1-SETUP.md)。
