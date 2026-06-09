from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from app.config import settings

# 全局 engine 和 session 工厂（应用级别单例）
engine=create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG #开发时打印每条 SQL，生产关闭。比直接写 True 灵活
)

SessionLocal=async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
'''
默认行为（expire_on_commit=True）：session.commit() 后，所有已加载的 ORM 对象的属性会被标记为"过期"。
下次访问这些属性时，SQLAlchemy 会自动发 SELECT 重新查询。

这在同步 FastAPI 中是合理的（防止 commit 后的数据不一致），但在异步 FastAPI 中会出问题：
asyncpg + SQLAlchemy 的异步模式要求不在不恰当的时候隐式发 SQL。
expire_on_commit=False 避免了 commit 后的隐式查询，也避免了著名的 "greenlet_spawn" 错误。
'''



#get_db是一个异步生成器
async def get_db()->AsyncGenerator[AsyncSession,None]:
    """每个请求获取一个独立的数据库会话

    使用方式:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with SessionLocal() as session: # 从工厂获取 session
        try:
            yield session #交给请求处理函数
            await session.commit()
            # 请求处理完后，自动回到这里，session 被 async with 关闭

        except Exception:
            await session.rollback()
            raise

'''

# 执行时序：
#   ① 进入 get_db，执行 async with，拿到 session
#   ② yield session → 跳到路由函数
#   ③ 路由函数使用 session 查询数据库
#   ④ 路由函数 return → 控制权回到 get_db
#   ⑤ 退出 async with → session 关闭，连接归还连接池

正常路径:
  yield session → 路由函数正常返回 → session.commit() → 关闭 session

异常路径:
  yield session → 路由函数抛出异常 → session.rollback() → 关闭 session → 异常继续传播

async with 块退出时自动调用 await session.close()。不需要手动写 finally: session.close()。


'''

'''
create_async_engine()          →  engine（全局唯一，管理连接池）
        │
        ▼
async_sessionmaker(engine)     →  session_factory（工厂函数，每次调用创建一个新 session）
        │
        ▼
session_factory()              →  session（每个请求一个，用完关闭）

对象	             生命周期	       数量	                类比
AsyncEngine	        应用启动到关闭	   1 个	            数据库连接池本身
async_sessionmaker	应用启动到关闭	   1 个	            连接池的"发卡机"
AsyncSession	    单个 HTTP 请求	  每个请求 1 个	    从连接池借的一张"卡"

一个 engine 维护一个连接池（比如 10 个连接），每次请求借一个连接，用完归还。这是数据库连接池的基本原理。
'''



'''
Q: 为什么 engine 在模块级别创建而不是在函数内？

Engine 内部管理连接池（默认 5 个连接），创建和销毁成本高。模块级变量保证导入时创建一次，进程存活期间复用。如果放在函数内，每次调用 get_db 都创建新 engine，连接池会爆炸。

Q: 后面的 main.py 如果用 lifespan 管理 engine，这里怎么改？

把 engine 和 SessionLocal 的创建移到 lifespan 中，通过 app.state 存储，get_db 从 app.state 取。但那是 Phase 1 最后一步的事。现在是让 deps.py 能独立工作，不依赖 main.py。耦合方向应该是 main.py → deps.py，不是反过来。


'''