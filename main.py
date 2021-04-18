from flask import Flask, render_template, redirect, request, make_response, session, abort, url_for
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.publications import Publication
from forms.users import RegisterForm, LoginForm
from forms.publications import AddPublicationForm

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data.additional_methods import is_latin, image_1600

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
    return render_template('index.html', title='home')


@app.route('/profile/<name>')
def profile(name):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()
    user.__init__()
    user_data = user.other_data
    return render_template('profile.html', title='profile', user_data=user_data)


is_view = False


@app.route('/add_publication', methods=['GET', 'POST'])
def add_publication():
    global is_view
    form = AddPublicationForm()

    if form.submit_view.data or form.submit.data:
        current_user.load_data()
        photo_name = f'id_{current_user.id}_pub_{len(current_user.other_data["publications"]) + 1}'

        if not is_view:
            image_1600(request.files['file'], photo_name)
            is_view = True

        if form.submit.data:
            is_view = False

            db_sess = db_session.create_session()
            publication = Publication()
            publication.user_id = current_user.id
            publication.filename_photo = photo_name
            publication.about = form.about.data

            db_sess.add(publication)
            db_sess.commit()

            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.load_data()
            user.other_data['publications'].append(photo_name)
            user.save_data()

            return redirect(f'/profile/{current_user.name}')
        else:
            return render_template('add_publication.html', title='add_publication', form=form, photo_name=photo_name)
    return render_template('add_publication.html', title='add_publication', form=form)


@app.route('/notification')
def notification():
    return render_template('notification.html', title='notification')


@app.route('/explore')
def explore():
    return render_template('explore.html', title='explore')


@app.route('/direct')
def direct():
    return render_template('direct.html', title='direct')


@app.route('/home')
def home():
    return render_template('home.html', title='home')


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

        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', form=form, title='Регистрация',
                                   message='Имя пользователя занято')

        if not is_latin(form.name.data):
            return render_template('register.html', form=form, title='Регистрация',
                                   message='Именах пользователя можно использовать только буквы(a-z), цифры, симбволы подчерикивания и точки')

        user = User()
        user.name = form.name.data
        user.full_name = form.full_name.data
        user.about = form.about.data
        user.email = form.email.data
        user.create_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        db_sess.query(User).filter(User.name == user.name).first().__init__()

        login_user(user, True)
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
