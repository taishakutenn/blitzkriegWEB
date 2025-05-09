"""Это файл в котором описаны модели базы данных"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.String(50), index=True, unique=True, nullable=False)
    email = sa.Column(sa.String(120), index=True, unique=True, nullable=False)
    hashed_password = sa.Column(sa.String(256), nullable=True)

    # Связь с дочерней таблицей
    levels = so.relationship("Level", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def avatar(self, size):
        """Этот метод генерирует url-адресс пользователя, на основе его почты, с помощью этого url
        адресса на сервере Gravatar хранится аватарка пользоватлея, если этой аватарки нет, с помощью
        параметра d в url-запроссе выставляется случайный аватар геометрического объекта"""

        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?s={size}&d=identicon"


class Level(db.Model):
    __tablename__ = "levels"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100), index=True, nullable=False)
    level_id = sa.Column(sa.Integer, nullable=False)
    copy_id = sa.Column(sa.Integer, nullable=True)
    is_completed = sa.Column(sa.Boolean, default=False)
    percent = sa.Column(sa.Integer, default=0)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=False)

    # Связь с дочерней таблицей
    stages = so.relationship("Stage", back_populates="level")

    # Связь с родительской таблицей
    user = so.relationship("User", back_populates="levels")


class Stage(db.Model):
    __tablename__ = "stages"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    number = sa.Column(sa.Integer)
    is_completed = sa.Column(sa.Boolean, default=False)
    level_id = sa.Column(sa.Integer, sa.ForeignKey("levels.id"), nullable=False)

    # Связь с дочерней таблицей
    runs = so.relationship("Run", back_populates="stage")

    # Связь с родительской таблицей
    level = so.relationship("Level", back_populates="stages")


class Run(db.Model):
    __tablename__ = "runs"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    percentages = sa.Column(sa.String, nullable=True)
    is_completed = sa.Column(sa.Boolean, default=False)
    stage_id = sa.Column(sa.Integer, sa.ForeignKey("stages.id"), nullable=False)

    # Связь с родительской таблицей
    stage = so.relationship("Stage", back_populates="runs")


# Функция для фласк-логина
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))