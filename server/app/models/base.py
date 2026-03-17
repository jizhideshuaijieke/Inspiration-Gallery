from sqlalchemy.orm import DeclarativeBase

#所有表模型共享的“根类”，Alembic 会从它拿到全量表元数据
class Base(DeclarativeBase):
    pass
