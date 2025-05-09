"""Это файл всех форм"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField, StringField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(), Length(3, 15)])
    email = EmailField("Email", validators=(DataRequired(), Email()))
    password = PasswordField("Пароль", \
                             validators=[DataRequired(), Length(6, 25),
                                         EqualTo("confirm_password", message="Пароли не совпадают")])
    confirm_password = PasswordField("Повторите пароль")
    submit = SubmitField("Зарегистрироваться")

    def validate_username(self, username):
        user = db.session.query(User).filter(User.username == username.data).first()
        if user:
            raise ValidationError('Пользователь с таким никнеймом уже сущесвует')

    def validate_email(self, email):
        user = db.session.query(User).filter(User.email == email.data).first()
        if user:
            raise ValidationError('Пользователь с таким email уже сущесвует')
