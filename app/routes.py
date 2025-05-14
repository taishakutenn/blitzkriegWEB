"""В этом файле находятся все обработчики маршрутов на сайте"""
from random import choices

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
import os
import asyncio
from urllib.parse import urlsplit
from is_safe_url import is_safe_url

from app import app, db
from app.forms import LoginForm, RegisterForm, EditForm, EditPasswordForm
from app.models import User, Level, Stage, Run
from app.pointercrateAPI import get_demonlist, get_lvl
from app.gdAPI import find_lvl, get_blitzkrieg

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.errorhandler(415)
def unsupported_media_type(error):
    """Эта ошибка происходит при попытке перейти на /save_state"""
    return redirect('/')


@app.route("/")
@app.route("/index")
def index():
    """Главная страница с топом уровней"""

    params = {"title": "Главная",
              'demonlist': asyncio.run(get_demonlist())}
    return render_template("index.html", **params)


@app.route("/save_state", methods=["GET", "POST"])
def save_state():
    """
    Сохранение текущей информации на странице с уровнем
    На страницу save_state перейти невозможно, так как перекидывает на index.
    Вызывается через Checkboxes.js при закрытии|переходе|обновлении вкладки /level/<lvl_id>
    """
    # Получаем и форматируем информацию из таблицы
    [level_name, level_id, copy_id], *row_runs = request.json
    level_id = level_id.split()[-1]
    table = []
    for run in row_runs:
        if 'Stage' in run[0]:
            table.append([run[1]])
        else:
            table[-1].append(run)

    # Получаем уровень
    lvl = db.session.query(Level).filter(Level.user == current_user, Level.level_id == level_id).first()

    # Добавляем уровень, если его нет в бд
    if lvl is None and 'True' in str(table):
        lvl = Level(name=level_name,
                    level_id=level_id,
                    copy_id=copy_id,
                    is_completed=False,
                    percent=0,
                    user_id=current_user.id)
        db.session.add(lvl)
        for number, runs in enumerate(table):
            stage = Stage(number=number,
                          is_completed=False,
                          level=lvl)
            db.session.add(stage)
            for percentages, is_completed in runs[1:]:
                run = Run(percentages=percentages,
                          is_completed=is_completed,
                          stage=stage)
                db.session.add(run)

    # Обновляем значения в бд
    if lvl:
        for stage in lvl.stages:
            stage.is_completed = table[stage.number][0]
            for n, run in enumerate(stage.runs):
                run.is_completed = table[stage.number][1:][n][1]

        # Измеряем, пройден ли уровень
        completed = len(db.session.query(Stage.is_completed).filter(
            Stage.is_completed == 1, Stage.level == lvl).all())
        all_runs = len(table)
        lvl.is_completed = completed == all_runs

    db.session.commit()
    return "none"


@app.route("/level/<lvl_id>", methods=["GET", "POST"])
def level(lvl_id):
    """
    Выводит всю информацию об уровне с id(GD) = lvl_id.
    Генерирует таблицу прогрессов на уровне, если уровня нет у current_user.levels
    """

    # Функция выполняет список асинхронных функций
    async def async_tasks(tasks):
        return [await task for task in asyncio.as_completed(tasks)]

    # Находим информацию об уровне
    gd = pointer = None
    for response in asyncio.run(async_tasks([get_lvl(lvl_id), find_lvl(lvl_id)])):
        if type(response) is dict:
            if 'song' in response.keys():
                gd = response
            else:
                pointer = response

    lvl = db.session.query(Level).filter(Level.user == current_user, Level.level_id == gd['id']).first()
    start_pos = asyncio.run(find_lvl(lvl.copy_id)) if lvl else None
    table = []
    if lvl is None:
        # Находим start_pos копию
        for response in asyncio.run(async_tasks([find_lvl(f'{gd['title']} startpos'[:20]),
                                                 find_lvl(f'{gd['title']} sp'[:20])])):
            if type(response) is dict:
                if response['title'].lower() == f'{gd['title']} startpos'[:20].lower():
                    start_pos = response
                    break
                else:
                    start_pos = response

        # Составление таблицы из копии
        if start_pos is not None:
            table = asyncio.run(get_blitzkrieg(start_pos['id']))

    else:
        # Составление таблицы из бд
        for stage in lvl.stages:
            table.append([])
            table[-1].append(stage.is_completed)
            for run in stage.runs:
                table[-1].append([run.percentages, run.is_completed])

    # Рендерим страницу
    params = {"title": gd['title'],
              "pointer_info": pointer,
              "gd_info": gd,
              "table": table,
              "start_pos": start_pos}

    return render_template("level_page.html", **params)


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

    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
        next_page = url_for('index')

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
        next_page_post = request.form.get("next")

        if next_page_post and is_safe_url(next_page_post, ['127.0.0.1:5000']):
            return redirect(next_page_post)

        return redirect(url_for("index"))

    params = {"title": "Авторизация", "form": form, "next": next_page}
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
        return redirect(url_for("login"))

    params = {"title": "Регистрация",
              "form": form}

    return render_template("register.html", **params)


@app.route("/users/<int:user_id>", methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    levels = db.session.query(Level).filter(Level.user == user).all()

    # Настройки для визуала / формочек
    form_edit_password = EditPasswordForm()
    form_edit = EditForm()
    params = {
        'title': 'Профиль',
        'form_edit': form_edit,
        'form_edit_password': form_edit_password,
        'user': user}
    param_active_tab_edit_password = {
        'edit_password': 'aria-selected=true tabindex=-1',
        'edit_password_active': 'active',
        'edit_password_show': 'show'
    }
    param_active_tab_my_profile = {
        'my_profile': 'aria-selected=true tabindex=-1',
        'my_profile_active': 'active',
        'my_profile_show': 'show'
    }
    active_tab = param_active_tab_my_profile

    # Изменение пароля
    if form_edit_password.validate_on_submit():
        active_tab = param_active_tab_edit_password
        if current_user.check_password(form_edit_password.password_check.data):
            if form_edit_password.password_new.data == form_edit_password.password_again.data:
                user = db.session.query(User).filter(User.email == current_user.email).first()
                user.set_password(form_edit_password.password_new.data)
                db.session.add(user)
                db.session.commit()
                return render_template('profile.html', **params, **active_tab, error_message='Успешно!')
            return render_template('profile.html', **params, **active_tab, error_message='Пароли не совпадают')
        return render_template('profile.html', **params, **active_tab, error_message='Неправильный пароль')
    elif (form_edit_password.password_check.data or
          form_edit_password.password_new.data or
          form_edit_password.password_again.data):
        return render_template('profile.html', **params, **param_active_tab_edit_password,
                               error_message='Не все поля заполнены!')

    # Изменение аватарки или имя пользователя
    if form_edit.validate_on_submit():
        user = db.session.query(User).get(current_user.id)
        if form_edit.source_image.data and form_edit.source_image.data.filename:
            alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            if user.source_image != 'default.png':
                os.remove(f'app/static/img/users_avatars/{user.source_image}')
            filename = f'{"".join(choices(alphabet, k=15))}.png'
            form_edit.source_image.data.save(f'app/static/img/users_avatars/{filename}')
            user.source_image = filename
        if form_edit.username.data:
            user.username = form_edit.username.data
        db.session.add(user)
        db.session.commit()
        return redirect(f'/users/{current_user.id}')

    return render_template('profile.html', **params, **active_tab)
