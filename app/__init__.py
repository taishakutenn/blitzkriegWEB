"""Это файл инициилизации всего приложения.
Тобишь, здесь создаётся точка входа в приложение app и подключаются все нужные зависимости
Если точнее, то здесь должны быть все импорты для создания Flask(__name__) и его корректной работы"""

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"

from app import routes, forms, models

