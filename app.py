from flask import Flask, flash, render_template, request, redirect, url_for, abort
from flask_login import LoginManager, current_user, login_user, logout_user, AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
import os
from werkzeug.security import generate_password_hash, check_password_hash

import requests

from models import Dish, Shopping_Cart, User, DishCardItems
from forms import (
    LoginForm,
    OrderForm,
    RegisterForm,
    RevisionForm,
    AddDishForm,
)

app = Flask(__name__)
app.secret_key = "123"
# app.config[
#     "SQLALCHEMY_DATABASE_URI"
# ] = "postgresql+psycopg2://postgres:root@localhost:5432/3sem_goiteens"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    app.root_path, "database.db"
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class AnonUser(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False
    
login_manager.anonymous_user = AnonUser

class UserLogin:
    def __init__(self, user_id: int | None = None, username: str | None = None):
        if user_id:
            self.user = db.session.execute(
                select(User).where(User.id == user_id)
            ).scalar_one()
        elif username:
            self.user = db.session.execute(
                select(User).where(User.username == username)
            ).scalar_one()
        else:
            raise TypeError("user_id or username args are required")

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user.id)
    
    @property
    def is_admin(self):
        return self.user.is_admin


@login_manager.user_loader
def load_user(user_id):
    try:
        return UserLogin(user_id=user_id)
    except NoResultFound:
        return


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = db.session.execute(
                select(User).where(User.username == form.username.data)
            ).scalar_one()
        except NoResultFound:
            flash("Нема такого користувача")
        else:
            if check_password_hash(user.password, form.password.data):
                user_login = UserLogin(user_id=user.id)
                login_user(user_login)
                return redirect(url_for("index"))
            flash("Неправильний пароль")
    return render_template("login.html", form=form)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        pw_hash = generate_password_hash(form.password.data)
        try:
            user = User(username=form.username.data, password=pw_hash)
            db.session.add(user)
            db.session.commit()
            shopping_cart = Shopping_Cart(user_id=user.id)
            db.session.add(shopping_cart)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Користувач вже існує з таким ім'ям")
        else:
            return redirect(url_for("index"))
    return render_template("signup.html", form=form)


@app.route("/dishes")
def dishes():
    dishes = db.session.execute(select(Dish)).scalars()
    return render_template("dishes.html", dishes=dishes)


@app.route("/shopping_cart", methods=["GET", "POST"])
def shopping_cart():
    if request.method == "POST":
        dish_id = request.form.get("dish_id")
        shopping_cart = db.session.execute(
            select(User).where(User.id == current_user.get_id())
        ).scalar_one()
        shopping_cart_id = shopping_cart.id
        dish_item = (
            db.session.query(DishCardItems)
            .filter(
                DishCardItems.shopping_cart_id == shopping_cart_id,
                DishCardItems.dish_id == dish_id,
            )
            .first()
        )
        if dish_item:
            db.session.delete(dish_item)
        db.session.commit()
    shopping_cart = db.session.execute(
        select(Shopping_Cart).where(Shopping_Cart.user_id == current_user.user.id)
    ).scalar_one()

    # summ
    return render_template("shopping_cart.html", shopping_cart=shopping_cart)


@app.route("/dishes/<int:dish_id>", methods=["GET", "POST"])
def show_user(dish_id: int):
    form = OrderForm()
    dish = db.session.execute(select(Dish).where(Dish.id == dish_id)).scalar_one()
    if form.validate_on_submit():
        shopping_cart = db.session.execute(
            select(Shopping_Cart).where(Shopping_Cart.user_id == current_user.get_id())
        ).scalar_one()
        dishitem = DishCardItems(
            dish=dish, shopping_cart=shopping_cart, amount=form.amount.data
        )
        db.session.add(dishitem)
        db.session.commit()
        return redirect(url_for("shopping_cart"))
    return render_template("dish_id.html", dish=dish, form=form)


# @app.route("/add_shopping/<int:dish_id>")
# def add_to_shopping(dish_id: int):
#     dish = db.session.execute(select(Dish).where(Dish.id == dish_id)).scalar_one()
#     shopping_cart = db.session.execute(
#         select(Shopping_Cart).where(Shopping_Cart.user_id == current_user.get_id())
#     ).scalar_one()
#     dishitem = DishCardItems(dish=dish, shopping_cart=shopping_cart)
#     db.session.add(dishitem)
#     db.session.commit()
#     return redirect(url_for("shopping_cart"))


# @app.route("/movie/<int:movie_id>", methods=["POST", "GET"])
# def show_movie_page(movie_id: int):
#     form = RevisionForm()
#     try:
#         movie = db.session.execute(
#             select(Dish).where(Dish.id == movie_id)
#         ).scalar_one()
#     except NoResultFound:
#         return "Такого фільму не існує"

#     if form.validate_on_submit():
#         user = current_user.user
#         print(user.password)
#         revision = Shopping_Cart(
#             user_id=user.id,
#             movie_id=movie_id,
#             rating=form.rating.data,
#             comment=form.comment.data,
#         )
#         db.session.add(revision)
#         db.session.commit()

#     return render_template("movie_page.html", movie=movie, form=form)


# def get_movie_by_kinopoisk(movie_id: int):
#     headers = {
#         "X-API-KEY": "f56131b4-c5d4-4081-b830-b2f5d91fb4e3",
#         "Content-Type": "application/json",
#     }
#     r = requests.get(
#         f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{movie_id}",
#         headers=headers,
#     )
#     if r.status_code != 200:
#         return None
#     data = r.json()
#     return data


@app.route("/add_dish", methods=["POST", "GET"])
def add_dish():
    try:
        is_admin = current_user.user.is_admin
    except AttributeError:
        is_admin = False
    if is_admin:
        form = AddDishForm()
        if form.validate_on_submit():
            dish = Dish(
                name=form.title.data,
                description=form.description.data,
                price=form.price.data,
                image_url=form.image_url.data,
            )
            db.session.add(dish)
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("add_dish.html", form=form)
    abort(401)


# @app.route("/confirm_film/<int:movie_id>", methods=["GET", "POST"])
# def confirm_film(movie_id: int):
#     movie = get_movie_by_kinopoisk(movie_id)
#     if not movie:
#         flash("Такого фільму не існує")
#         return redirect(url_for("add_movie"))
#     form = ConfirmKinopoiskMovieForm(
#         title=movie["nameOriginal"],
#         description=movie["description"],
#         image_url=movie["posterUrl"],
#     )
#     if form.validate_on_submit():
#         d = Dish(
#             name=form.title.data,
#             description=form.description.data,
#             image_url=form.image_url.data,
#         )
#         try:
#             db.session.add(m)
#             db.session.commit()
#         except IntegrityError:
#             flash("Сталася помилка під час додавання фільму")
#             return redirect(url_for("add_movie"))
#         else:
#             return redirect(url_for("show_movie_page", movie_id=m.id))
#     return render_template("confirm_movie.html", movie=movie, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


app.run(debug=True)
