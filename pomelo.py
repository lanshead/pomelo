import sqlite3
import os
import hashlib
from FDataBase import FDataBase
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort, g

DATABASE = '/tmp/flsk_website.db'
DEBUG = True
SECRET_KEY = 'aete%#@%aglaghlsdhl124215%#@%#gdlsgl'
# USERNAME = 'admin'
# PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsk_website.db')))

# Имитация данных о текущих задачах из БД
current_tasks = {'task1': {'time_create': 1, 'time_action': 11, 'iscycle': True},
                 'task2': {'time_create': 2, 'time_action': 22, 'iscycle': False},
                 'task3': {'time_create': 3, 'time_action': 33, 'iscycle': True},
                 'task4': {'time_create': 4, 'time_action': 44, 'iscycle': False},
                 'task5': {'time_create': 5, 'time_action': 55, 'iscycle': True}}


# >>>Навигация по сайту
@app.route('/')
def index():
    if 'userLogged' not in session:
        return render_template('login.html', h1='Авторизация')
    return render_template('index.html', h1='Задачи', current_tasks=current_tasks)

@app.route('/test')
def test():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('test.html', users=dbase.getLogPass('test2'))

@app.route('/login', methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        db = get_db() #  коннект к базе
        dbase = FDataBase(db).getLogPass(request.form['username']) # получение из базы значения пользователя и его хеш-пароля в виде [dict()]
        if dbase: #  eсли dbase нашла пользователя
            if hashlib.scrypt(request.form['pass'].encode(), salt='mysalt'.encode(), n=8, r=512, p=4, dklen=32).hex() == dbase[0]['_pass']: # хешируем введенный пароль и сравниваем тем хешем, который есть взят из базы
                session['userLogged'] = request.form['username'] # заполняем значение сессии о том, что пользователь авторизован
                return redirect(url_for('profile', username=session['userLogged'])) # перенаправляем пользователя на страницу профиля
            flash('Ошибка ввода логина и/или пароля', category='error')
        else:
            flash('Ошибка ввода логина и/или пароля', category='error')
    return render_template('login.html', h1='Авторизация') # возвращаем страницу авторизации.


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)

    return render_template('index.html', h1='Задачи', current_tasks=current_tasks)


# >>>Взаимодействие с БД
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    '''function for create DB'''
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''connect to DB, if it is not installed'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    '''close DB, if it is installed'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


# >>>Обработки ошибок
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', h1='Страница не найдена'), 404


@app.errorhandler(401)
def pageNotAutorized(error):
    return render_template('page401.html', h1='Вы не авторизованы'), 401


if __name__ == '__main__':
    app.run(debug=True)

# @app.route('/login', methods=["POST", "GET"])
# def login():
#     if request.method == 'POST':
#         if request.form['username'] == 'admin' and request.form['pass'] == '12345':
#             flash('Успешно', category='success')
#         else:
#             flash('Ошибка', category='error')
#     return render_template('login.html', h1='Авторизация')
