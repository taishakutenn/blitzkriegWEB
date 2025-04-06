"""Это файл конфигов
В нём мы берём значения из переменных окружения и подставляем в наше приложение"""

import os
from dotenv import load_dotenv

load_dotenv() # Импортируем и используем функцию для автоматического считывания значений из файла .env
base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "never_gues_my_key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(base_dir, "app.db")
    FLASK_APP = os.environ.get("FLASK_APP") or os.path.join(base_dir, "run.py")
