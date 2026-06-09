'''
项目中所有表（员工、项目、考勤、知识库……）都需要重复定义相同的字段：

id  +  created_at  +  updated_at  +  is_deleted  +  deleted_at
如果每个 Model 类都手写一遍这 5 个字段，带来的问题是：

一致性风险 — 哪天有人忘了加 is_deleted，那张表的软删除就不生效
规范变更成本高 — 如果要给所有表加一个 created_by 字段，需要改 N 个文件
代码臃肿 — 每个 Model 前 20 行都是重复的样板代码

base.py 的职责：定义一个公共基类，让所有业务 Model 继承它，自动获得统一的通用字段。
'''
from datetime import datetime

from sqlalchemy import BigInteger,Boolean,DateTime,func,text
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类，所有 Model 的最终父类"""
    pass


class BaseModel(Base):
    """所有业务表的公共基类，包含通用字段"""
    '''
    #字段名:Mapped[Python类型]=mapped_column(
            sql数据类型,
            其它参数...
    )
    '''

    __abstract__=True

    id:Mapped[int]=mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True #自增
    )

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False #不能为空
    )

    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    is_deleted:Mapped[bool]=mapped_column(
        Boolean,
        server_default=text("FALSE"),
        nullable=False
    )

    deleted_at:Mapped[datetime|None]=mapped_column(
        DateTime(timezone=True),
        server_default=None,
        nullable=True
    )
'''
Q: 如果某张表不需要 is_deleted（比如 audit_logs 是仅追加的），怎么办？

那就不要继承 BaseModel，直接继承 Base，然后手动定义需要的字段。
BaseModel 不是强制的——它是一个便捷工具，不是枷锁。

Q: 为什么不用 UUID 做主键？

UUID 做主键有两个问题：
1) BIGSERIAL 索引比 UUID 索引更紧凑（8 bytes vs 16 bytes）；
2) 插入时 BIGSERIAL 是单调递增的，B-tree 索引写入效率高，UUID 随机性导致页分裂。对外暴露时可以用一个额外的 public_id: UUID 字段，主键还是用 BIGSERIAL。
'''

    
