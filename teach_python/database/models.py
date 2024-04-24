import sqlalchemy
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    update: Mapped[DateTime] = mapped_column(DateTime,default=func.now(), onupdate=func.now())


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(150), nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.Text)
    price: Mapped[float] = mapped_column(
        sqlalchemy.Float(asdecimal=True), nullable=False
    )
    image: Mapped[str] = mapped_column(sqlalchemy.String(150))
