"""В этом файле будут находиться все обработчики маршрутов на сайте"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
import os
import asyncio

from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import User
from app.other import get_demonlist


@app.route("/")
@app.route("/index")
def index():
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    params = {"title": "Главная",
              'demonlist': asyncio.run(get_demonlist())}
    # {'id': 562,
    # 'position': 1,
    # 'name': 'Tidal Wave',
    # 'requirement': 72,
    # 'video': 'https://www.youtube.com/watch?v=9fsZ014qB3s',
    # 'thumbnail': 'https://i.ytimg.com/vi/9fsZ014qB3s/mqdefault.jpg',
    # 'publisher': {'id': 56892, 'name': 'OniLink', 'banned': False},
    # 'verifier': {'id': 53408, 'name': '[POB2P] Zoink', 'banned': False},
    # 'level_id': 86407629}
    return render_template("index.html", **params)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Тут уточняю, на страницу логина можно попасть, если перейти на какую-либо страницу, на которой
    обязательно требуется иметь вход в аккаунт на сайте, за это отвечает декоратор @login_required
    при этом, когда нас с такой страницы перенаправляет на страницу логина, то к URL запросу добавляется
    параметр 'next'. Именно поэтому, внизу есть часть кода с next_page
    Подробнее здесь -> https://habr.com/ru/articles/808091/
    """

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if not user:
            flash("Такого пользователя не существует")
            return redirect(url_for("login"))

        if not user.check_password(form.password.data):
            flash("Введён неверный пароль")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")

        if next_page:
            return redirect(next_page)

        return redirect(url_for("index"))

    params = {"title": "Авторизация",
              "form": form}

    return render_template("login.html", **params)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("index"))

    params = {"title": "Регистрация",
              "form": form}

    return render_template("register.html", **params)
