#lanshead import
import sqlite3
import os
import hashlib
import json
from sourcescript import compare_count_pos
from forms import ReportTest1
from FDataBase import FDataBase
from flask import Flask, render_template, request, flash, redirect, url_for, session, abort, g
# biteANDrun import
# import datetime
# import time
# from pymssql import connect
# import requests
# from obj_env.obj_classes import PositionComp
# from datetime import timedelta, datetime

DATABASE = '/tmp/flsk_website.db'
DEBUG = True
SECRET_KEY = 'aete%#@%aglaghlsdhl124215%#@%#gdlsgl'
# USERNAME = 'admin'
# PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsk_website.db')))


def config_rep_test1(tsk_name):
    db = get_db()
    dbase = FDataBase(db)
    return json.loads(dbase.getConfigTest1(tsk_name)[0][0])


# >>>Навигация по сайту
@app.route('/')
def index():
    if 'userLogged' not in session:
        return render_template('login.html', h1='Авторизация')
    db = get_db()
    dbase = FDataBase(db)
    actions = dbase.fromActions()
    configs = {}
    for task in actions:
        configs[f'{task[1]}']=json.loads(task[6])
    return render_template('index.html', h1='Задачи', actions=actions, configs=configs)


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
        db = get_db()  # коннект к базе
        dbase = FDataBase(db).getLogPass(
            request.form['username'])  # получение из базы значения пользователя и его хеш-пароля в виде [dict()]
        if dbase:  # eсли dbase нашла пользователя
            if hashlib.scrypt(request.form['pass'].encode(), salt='mysalt'.encode(), n=8, r=512, p=4, dklen=32).hex() == \
                    dbase[0]['_pass']:  # хешируем введенный пароль и сравниваем тем хешем, который есть взят из базы
                session['userLogged'] = request.form[
                    'username']  # заполняем значение сессии о том, что пользователь авторизован
                return redirect(url_for('index', username=session[
                    'userLogged']))  # перенаправляем пользователя на страницу профиля
            flash('Ошибка ввода логина и/или пароля', category='error')
        else:
            flash('Ошибка ввода логина и/или пароля', category='error')
    return render_template('login.html', h1='Авторизация')  # возвращаем страницу авторизации.


@app.route("/add_task", methods=["POST", "GET"])
def addTask():
    '''Рендерит страницу для указания наименования и выбора отчета. При нажатии кнопки "Далее" редиректит на
    страницу соответствующую отчета для заполнения дополнительных параметров'''
    if 'userLogged' not in session:
        abort(401)
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        if len(request.form['task_name']) > 4 and request.form['report_name'] == 'test1':
            session['task_name'] = request.form['task_name']  # сохраняем в сессии имя отчета
            return redirect(url_for('report_for_test1'))
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_task.html', h1='Добавить задачу', reports=dbase.fromReports())


@app.route('/report_for_test1', methods=['GET', 'POST'])
def report_for_test1():
    '''Заполнение данных для конкретного отчета.'''
    if 'userLogged' not in session:
        abort(401)

    db = get_db()
    dbase = FDataBase(db)
    form = ReportTest1()
    # print(form.data)
    if form.validate_on_submit():
        # ГДЕ-ТО ЗДЕСЬ МЫ ДОЛЖНЫ СДЕЛАТЬ ЧТО-ТО С ШЕДУЛЕРОМ
        configs = json.dumps(
            {'user': request.form['user'],
             'usr_pass': request.form['usr_pass'],
             'db_adress': request.form['db_adress'],
             'db_login': request.form['db_login'],
             'db_pass': request.form['db_pass'],
             'db_name': request.form['db_name'],
             'time_interval': request.form['time_interval'],
             'tm_begin': request.form['tm_begin'],
             'dt_begin': request.form['dt_begin'],
             'tm_end': request.form['tm_end'],
             'dt_end': request.form['dt_end']
             })
        # ИЛИ ЗДЕСЬ (А МОЖЕТ И ПОТОМ ЗАБРАВ ИНФУ ИЗ БД)
        dbase.addTask(session['task_name'], 'test1', 'compare_count_pos.py', configs, isactive=1, descript=None)
        return redirect(url_for('index'))
    # print(form.validate_on_submit(), request.form['time_interval'], request.form['tm_begin'], request.form['dt_begin'], request.form['tm_end'], request.form['dt_end'], sep='\n')
    return render_template('report_for_test1.html', h1='Задача для test1', form=form)


@app.route('/test1', methods=['GET', 'POST'])
def create_now():
    if 'userLogged' not in session:
        abort(401)
    db = get_db()
    dbase = FDataBase(db)
    tsk_name = [v for v in request.args.values()][0]
    config = json.loads(dbase.getConfigTest1(tsk_name)[0]['configs'])
    job = compare_count_pos.compare_positions(user=config['user'],
                            usr_pass=config['usr_pass'],
                            db_address=config['db_adress'],
                            db_login=config['db_login'],
                            db_pass=config['db_pass'],
                            db_name=config['db_name'])
    dbase.addJob(tsk_name, job[0], job[1])
    return render_template('job_output.html', h1='Задача выполнена', output=job[1])


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', h1='Задачи', actions=dbase.fromActions())


@app.route("/logout")
def logout():
    if 'userLogged' in session:
        session.clear()
    abort(401)


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
