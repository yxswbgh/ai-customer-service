from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import sys
from pathlib import Path

# 把 server/ 目录加入 Python 路径，让 app 模块可导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.models.base import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL_SYNC,  # 加这一行，覆盖 alembic.ini 的空值
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
    


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

'''
为什么 alembic init -t async 是一个容易中招的选项？

Alembic 官方提供了 -t async 模板，但它做的事情其实很有限：只是把同步引擎创建换成了异步引擎创建，然后用 asyncio.run() 包了一层。DDL 操作（ALTER TABLE 这类）在数据库层面就是同步执行的，异步包装不会带来性能提升，反而引入了两个复杂度：

异步/同步驱动不匹配时就会报你刚才遇到的错误
asyncio.run() 内部创建新的事件循环，可能与 FastAPI 的事件循环产生嵌套问题（虽然在 alembic CLI 中不会，但如果你在代码中调用 alembic API 就会碰到）
经验法则：迁移工具用同步连接，业务代码用异步连接。这个模式在 Django + Celery、Flask + gevent 等场景中都成立——schema 迁移不需要、也不应该依赖异步框架。
'''
