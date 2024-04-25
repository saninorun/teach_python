import sqlalchemy
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    update: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class Banner(Base):
    __tablename__ = "banner"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(15), unique=True)
    image: Mapped[str] = mapped_column(sqlalchemy.String(150), nullable=True)
    description: Mapped[str] = mapped_column(sqlalchemy.Text, nullable=True)


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(150), nullable=True)


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sqlalchemy.String(150), nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.Text)
    price: Mapped[float] = mapped_column(
        sqlalchemy.Float(asdecimal=True), nullable=False
    )
    image: Mapped[str] = mapped_column(sqlalchemy.String(150))
    category_id: Mapped[int] = mapped_column(
        sqlalchemy.ForeignKey("category.id", ondelete="CASCADE"), nullable=False
    )

    category: Mapped[Category] = relationship(backref="product")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(sqlalchemy.String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(sqlalchemy.String(150), nullable=True)
    phone: Mapped[str] = mapped_column(sqlalchemy.String(13), nullable=True)


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey('user.user_id', ondelete='CASCADE'),nullable=False)
    product_id: Mapped[int] = mapped_column(sqlalchemy.ForeignKey('product.id', ondelete='CASCADE'),nullable=False)
    quantity: Mapped[int]

    user: Mapped['User'] = relationship(backref='cart')
    product: Mapped['Product'] = relationship(backref='cart')

