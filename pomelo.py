from flask import Flask, render_template, request, flash, redirect, url_for, session, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aete%#@%aglaghlsdhl124215%#@%#gdlsgl'

# Имитация данных о текущих задачах из БД
current_tasks = {'task1': {'time_create': 1, 'time_action': 11, 'iscycle': True},
                 'task2': {'time_create': 2, 'time_action': 22, 'iscycle': False},
                 'task3': {'time_create': 3, 'time_action': 33, 'iscycle': True},
                 'task4': {'time_create': 4, 'time_action': 44, 'iscycle': False},
                 'task5': {'time_create': 5, 'time_action': 55, 'iscycle': True}}


@app.route('/')
def index():
    if 'userLogged' not in session:
        return render_template('login.html', h1='Авторизация')
    return render_template('index.html', h1='Задачи', current_tasks=current_tasks)


@app.route('/login', methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['pass'] == '12345':
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))
        else:
            flash('Ошибка ввода логина и/или пароля', category='error')
    return render_template('login.html', h1='Авторизация')


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)

    return render_template('index.html', h1='Задачи', current_tasks=current_tasks)


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
