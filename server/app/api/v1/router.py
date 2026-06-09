from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

router=APIRouter()

@router.get("/health")
async def health_check(db:AsyncSession=Depends(get_db)): #通过deps.py中写的get_db获取Asyncsession（从连接池中获取一个）
    """健康检查 — 返回服务状态和数据库连通性"""
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status":"ok",
            "database":"connected",
            "version":"0.1.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status":"error",
                "database":"disconnected",
                "error":str(e)
            }
        )

'''
Phase 2 添加问答、知识库等端点时，每个功能模块拆到独立文件（qa.py、knowledge.py），router.py 通过 include_router 聚合它们。

每个功能模块有自己的 router，顶层 router 负责组装。

'''

'''
为什么用 text("SELECT 1") 而不是 ORM 查询？

health check 的目的是测试数据库连接是否可用，不是测试 ORM 是否正常。
SELECT 1 是 PostgreSQL 里最快的查询——不需要表，不涉及 ORM mapping，纯粹的连接验证。
'''


'''
为什么 router = APIRouter() 不带 prefix？
# 方式 A: router 自己带 prefix
router = APIRouter(prefix="/api/v1")

# 方式 B: main.py include 时指定 prefix（推荐）
app.include_router(router, prefix="/api/v1")

方式 B 更好，因为 router.py 只管路由分组，不在乎自己挂在哪。哪天要加 v2 版本，router 内部的代码一行不改，只在 main.py 里挂不同 prefix。
'''

'''
为什么异常返回 503 而不是 500？

状态码	                      含义	                                场景
503 Service Unavailable	    服务暂时不可用，通常会自动恢复	    数据库挂了，重连后会好
500 Internal Server Error	服务器内部错误，不预期恢复	        代码 bug

负载均衡器看到 503 会停止转发流量，看到 500 可能不会。
Health check 的语义是"准备好服务了吗？"，没准备好 = 503。

'''