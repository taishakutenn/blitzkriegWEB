"""В этом файле будут находиться все обработчики маршрутов на сайте"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import User


@app.route("/")
@app.route("/index")
# @login_required  # Декортаор определящий, нужен ли здесь быть залогиненмы или нет
def index():
    params = {"title": "Главная"}

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Тут уточняю, на страницу логина можно попасть, если перейти на каку-либо страницу, на которой
    обязтаельно требуется иметь вход в аккаунт на сайте, за это отвечает декоратор @login_required
    при этом, когда нас с такой страницы перенапрвляет на страницу логина, то к URL запросу добавляется
    параметр 'next'. Именно поэтмоу, внизу есть часть кода с next_page
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
