"""Это файл всех форм"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField, StringField, EmailField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField("Имя пользователя", validators=[DataRequired(), Length(3, 15)])
    email = EmailField("Email", validators=(DataRequired(), Email()))
    password = PasswordField("Пароль", validators=[DataRequired(), Length(6, 25),
                                                   EqualTo("confirm_password", message="Пароли не совпадают")])
    confirm_password = PasswordField("Повторите пароль")
    submit = SubmitField("Зарегистрироваться")


class EditForm(FlaskForm):
    source_image = FileField('Изображение профиля', )
    username = StringField('Имя пользователя')
    submit = SubmitField('Сохранить')


class EditPasswordForm(FlaskForm):
    password_check = PasswordField('Старый пароль', validators=[DataRequired()])
    password_new = PasswordField('Новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Изменить')
