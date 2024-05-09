from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    PasswordField,
    SelectField,
    HiddenField,
    DecimalField,
)
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms.fields import IntegerField


class LoginForm(FlaskForm):
    username = StringField(
        "Username: ",
        validators=[
            DataRequired(),
            Length(5, 32, message="Це поле має містити в собі мін 5, макс 32 символи"),
        ],
    )
    password = PasswordField("Password: ", validators=[DataRequired(), Length(8, 32)])


class RegisterForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired(), Length(5, 32)])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(8, 32)])
    password_rep = PasswordField("Password: ", validators=[EqualTo("password")])


class RevisionForm(FlaskForm):
    comment = StringField("Comment: ", validators=[Length(0, 300)])
    rating = SelectField(
        "Rating: ",
        # choices=[("1", "1/5"), ("2", "2/5"), ("3", "3/5"), ("4", "4/5"), ("5", "5/5")],
        choices=[(str(x), str(x) + "/5") for x in range(1, 6)],
        validators=[DataRequired()],
    )


# class AddDish(FlaskForm):
#     name = StringField("Title: ", validators=[DataRequired()])


class AddDishForm(FlaskForm):
    title = StringField("Введи назву: ", validators=[DataRequired()])
    description = StringField("Введи опис: ", validators=[DataRequired()])
    price = DecimalField("Введи ціну (за 1кг): ", validators=[DataRequired()])
    image_url = StringField("Посилання на картинку: ", validators=[DataRequired()])


class OrderForm(FlaskForm):
    amount = IntegerField(render_kw={"value": 1, "min": 1, "max": 20, "step": 1})
