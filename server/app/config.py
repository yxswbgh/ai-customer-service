from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件和环境变量读取"""

    # ── 应用基础配置 ──
    APP_NAME: str = "ai-customer-service"
    APP_ENV: str = "development" #phase1只有development
    APP_DEBUG: bool = True
    APP_PORT: int = 8000

    # ── 数据库配置 ──
    '''数据库连接串包含密码，绝不应该在代码中有默认值'''
    '''在.env中'''
    DATABASE_URL: str = ""  #asyncpg驱动 FastAPI 异步请求处理，AsyncSession
    DATABASE_URL_SYNC: str = "" #Alembic 迁移（alembic 不支持 async

    # ── 安全配置 ──
    '''SECRET_KEY 在开发环境用固定值没问题，但生产环境必须通过环境变量覆盖。'''
    SECRET_KEY: str = "dev-secret-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config=ConfigDict(
        env_file=".env", #相对路径，相对于执行 Python 的工作目录（即 server/）
        env_file_encoding='utf-8',
        case_sensitive=True #字段名区分大小写。默认 Pydantic 是 case-insensitive 的，但数据库连接串的参数可能包含大小写敏感的值，显式声明更安全
    )


settings=Settings()
'''
Settings() 的初始化会读 .env 文件、解析环境变量，这个过程应该只做一次。
其他模块通过 from app.config import settings 拿到的是同一个实例，.env 只会被读一次。
'''
'''
如果运行时改了环境变量，settings 不会自动更新。
这是预期行为——配置应该在进程启动时确定，运行时不变化。
'''