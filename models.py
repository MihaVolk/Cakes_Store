from sqlalchemy import INTEGER, TEXT, Column, ForeignKey, Table, BOOLEAN, DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import expression
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class Shopping_Cart(Base):
    __tablename__ = "Shopping_Cart"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("users.id"), unique=True)
    dishes: Mapped[list["DishCardItems"]] = relationship(back_populates="shopping_cart")
    user: Mapped["User"] = relationship(back_populates="shopping_cart")

    @property
    def price(self):
        summ = 0
        for dish in self.dishes:
            summ += dish.dish.price * dish.amount
        return summ


class DishCardItems(Base):
    __tablename__ = "DishCardItems"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    dish_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("dishes.id"))
    shopping_cart_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("Shopping_Cart.id")
    )
    dish: Mapped["Dish"] = relationship()
    shopping_cart: Mapped[Shopping_Cart] = relationship(back_populates="dishes")
    amount: Mapped[int] = mapped_column(INTEGER, default=1)

    @property
    def price(self):
        summ = self.amount * self.dish.price
        return summ


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(TEXT, nullable=True, unique=True)
    password: Mapped[str] = mapped_column(TEXT, nullable=True)
    is_admin: Mapped[bool] = mapped_column(BOOLEAN, default=expression.false())
    shopping_cart: Mapped[Shopping_Cart] = relationship(back_populates="user")


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(TEXT)
    description: Mapped[str] = mapped_column(TEXT, default="empty")
    price: Mapped[Decimal] = mapped_column(DECIMAL, server_default="0")
    image_url: Mapped[str] = mapped_column(TEXT, nullable=True)
    # @property
    # def rating(self) -> float:
    #     sum_of_revision = 0.0

    #     for revision in self.revisions:
    #         sum_of_revision += revision.rating

    #     try:
    #         return round(sum_of_revision / len(self.revisions), 2)
    #     except ZeroDivisionError:
    #         return 0.0
