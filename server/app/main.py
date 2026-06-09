from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.deps import engine
from app.api.v1.router import router as v1_router
#所以 main.py 导入 router 时，整条依赖链被触发：
#import router → import deps → create_async_engine(settings.DATABASE_URL)
#这意味着 engine 在 uvicorn app.main:app 加载模块时就已经创建了，不需要在 lifespan 里手动创建 engine。
from app.config import settings
from app.middleware.cors import setup_cors
from app.utils.logger import get_logger,setup_logging

logger=get_logger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    """应用生命周期管理 — startup: 配置日志，shutdown: 关闭连接池"""
    # Startup
    setup_logging() #初始化日志
    logger.info("%s starting on port %s",settings.APP_NAME,settings.APP_PORT) #打印启动信息
    yield
    #Shutdown
    logger.info("%s shutting down",settings.APP_NAME)
    await engine.dispose() #关闭db连接池
    logger.info("Database connection pool closed") #打印关闭信息
'''
yield 之前的代码在应用启动时执行，yield 之后的代码在应用关闭时执行。
yield 的位置把 startup 和 shutdown 逻辑分开。
'''


app=FastAPI(
    title=settings.APP_NAME,
    description="AI 智能客服系统 — 企业级内部智能问答平台",
    version="0.1.0",
    lifespan=lifespan
)

#注册中间件
setup_cors(app)

'''
中间件按注册顺序逆序执行（洋葱模型）。
CORS 中间件应该在最外层（最先注册 = 最后执行 = 最先处理请求头）。
路由注册顺序影响的是 Swagger 文档中的显示顺序，不影响请求处理。
不过习惯上是先配好中间件，再挂路由。

'''

#注册路由
app.include_router(v1_router,prefix="/api/v1")

'''
模块级 vs lifespan
区分原则：同步的一次性配置放模块级，需要 await 的或者需要在关闭时清理的放 lifespan。
'''



'''
main.py是整个 FastAPI 应用的装配车间。
前面写好的所有模块——config、logger、cors、deps、router——都是独立的零件，
main.py 把它们组装成一个可以启动的应用。


main.py 的调用顺序：

uvicorn app.main:app
        │
        ▼
    模块被导入，全局代码执行
        │
        ├── setup_cors(app)          ← 注册中间件
        ├── include_router(...)       ← 注册路由
        │
        ▼
    应用启动，lifespan 开始
        │
        ├── setup_logging()          ← 配置日志
        ├── engine 已就绪             ← deps.py 导入时创建
        │
        ▼
    应用就绪，等待请求
        │
        ▼
    应用关闭，lifespan 结束
        │
        └── engine.dispose()         ← 关闭连接池


main.py ── 装配层
  ├── lifespan: logger 初始化 + engine 关闭
  ├── setup_cors(app)
  └── include_router(v1_router, prefix="/api/v1")
        │
        └── router.py ── 路由层
              └── GET /health (Depends: get_db)
                    │
                    └── deps.py ── 依赖注入层
                          ├── engine (全局连接池)
                          ├── SessionLocal (session 工厂)
                          └── get_db() (AsyncGenerator)

config.py ── 配置层
logger.py ── 日志层
middleware/cors.py ── 中间件层
models/base.py ── 数据模型层

'''


'''

为什么要配代理？
你现在有两个服务器在跑：


localhost:8000  →  FastAPI 后端（/api/v1/health）
localhost:5173  →  Vite 前端（/）
前端页面 localhost:5173 发 fetch('/api/v1/health') 会请求到 Vite 服务器，
Vite 收到后因为没有 /api 的路由，返回 404。
代理的作用是：Vite 收到 /api 开头的请求时，转发给 localhost:8000，不再当作前端路由处理。



'''