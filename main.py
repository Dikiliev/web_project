from flask import Flask, render_template, redirect, request, make_response, session, abort
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from forms.users import RegisterForm, LoginForm
from forms.top import DropdownForm
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

# Флаги
is_open_dropdown = False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    print(is_open_dropdown)
    form_dropdown = DropdownForm()
    if form_dropdown.validate_on_submit():
        print('sumbit')
        return render_template('index.html', title='home', form_dropdown=form_dropdown)
    return render_template('index.html', title='home', form_dropdown=form_dropdown)


def method_1():
    print('method_1')


@app.route('/profile/<name>')
def profile(name):
    return render_template('profile.html', title='profile')


@app.route('/explore')
def explore():
    return 'Explore'


@app.route('/direct')
def direct():
    return 'Direct'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, title='Регистрация', message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, title='Регистрация',
                                   message='Почта уже зарегистрирована')
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.create_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', form=form, title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            (User.name == form.name_or_email.data) | (User.email == form.name_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', title='Авторизация', form=form,
                               message='Неправильные данные для авторизации')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init('db/blogs.sqlite')
    db_sess = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
