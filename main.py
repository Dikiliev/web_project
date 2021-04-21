from flask import Flask, render_template, redirect, request, make_response, session, abort, url_for
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.publications import Publication
from forms.users import RegisterForm, LoginForm, EditProfileForm, ProfileForm
from forms.publications import AddPublicationForm
from forms.search import SearchForm

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from data.additional_methods import is_latin, image_size, random_list

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
    return render_template('index.html', title='Home')


@app.route('/profile/<name>', methods=['GET', 'POST'])
def profile(name):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()
    current_user.load_data()
    curr_user_data = current_user.other_data
    form = ProfileForm()
    if form.validate_on_submit():
        pass
    if user is None:
        return render_template('profile.html', title='profile', user_data=False)
    user.__init__()
    user_data = user.other_data
    return render_template('profile.html', title='profile', form=form, user=user, user_data=user_data, curr_user_data=curr_user_data)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        user.name = form.name.data
        user.full_name = form.full_name.data
        user.about = form.about.data

        user.email = form.email.data
        user.phone = form.phone.data

        if request.files and request.files['file']:
            file = request.files['file']

            if 'default' in user.filename_photo:
                photo_name = f'user_data/profile_photos/id_{user.id}_1_.png'
            else:
                # Для создания нового пути ( браузер показывал старое фото из за кеширования)
                photo_name = user.filename_photo
                num = int(photo_name.split('_')[-2]) + 1
                length = len(str(num - 1))
                photo_name = list(photo_name)
                photo_name[-6:-6 + length] = str(num)
                photo_name = ''.join(photo_name)

            image_size(request.files['file'], photo_name)
            user.filename_photo = photo_name

        db_sess.commit()
        load_user(user.id)

        return redirect(f'/profile/{user.name}')

    form.name.data = current_user.name
    form.full_name.data = current_user.full_name
    form.about.data = current_user.about
    form.email.data = current_user.email
    form.phone.data = current_user.phone

    current_user.load_data()
    user_data = current_user.other_data

    return render_template('edit_profile.html', title='Изменить профиль', form=form, user_data=user_data)


@app.route('/search', methods=['GET', 'POST'])
def search_user():
    form = SearchForm()
    if form.validate_on_submit():
        name = form.name.data  # Введенная пользователем имя (часть имени)
        db_sess = db_session.create_session()

        # Пользаветели чьи имена начинаются на name
        users = db_sess.query(User).filter((User.name.like(f'{name}%')) | (User.full_name.like(f'{name}%'))).all()
        # Добавление пользаветелей чьич именах есть name
        users += db_sess.query(User).filter(User.id.notin_([user.id for user in users]),
                                            (User.name.like(f'%{name}%')) | (User.full_name.like(f'%{name}%'))).all()

        return render_template('search.html', title='search', form=form, users=users)

    return render_template('search.html', title='Поиск', form=form)


is_view = False


@app.route('/add_publication', methods=['GET', 'POST'])
def add_publication():
    global is_view
    form = AddPublicationForm()

    if form.submit_view.data or form.submit.data:
        current_user.load_data()  # Загрузка дополнительных данных пользователя

        # Создание пути к файлу
        photo_name = f'user_data/publications/id_{current_user.id}_pub_{len(current_user.other_data["publications"]) + 1}.png'

        # Создать фотография если она не создана
        if not is_view:
            image_size(request.files['file'], photo_name)
            is_view = True

        # Если нажата кнопка "Опубликовать"
        if form.submit.data:
            is_view = False

            # Создание публикации...
            db_sess = db_session.create_session()
            publication = Publication()
            publication.user_id = current_user.id
            publication.filename_photo = photo_name
            publication.about = form.about.data

            db_sess.add(publication)
            db_sess.commit()

            # Загрузка публикации в дополнительные файлы пользователя (Сделано для удобства,
            # что бы при посещении профиля не искали его публикации среди всех других сещуствующих)
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.load_data()
            user.other_data['publications'].insert(0, photo_name)
            user.save_data()

            return redirect(f'/profile/{current_user.name}')
        # Иначе (Нажата кнопка "Просмореть")
        else:
            # Показ фотографии
            return render_template('add_publication.html', title='add_publication', form=form, photo_name=photo_name)
    return render_template('add_publication.html', title='Добавить новость', form=form)


@app.route('/show_publication', methods=['GET', 'POST'])
def show_publication():
    return render_template('publication.html', title='Публикации')


@app.route('/notification')
def notification():
    return render_template('notification.html', title='Уведомления')


@app.route('/explore')
def explore():
    db_sess = db_session.create_session()
    # Достаем все публикации кроме публкации текущего пользователя
    publications = db_sess.query(Publication).filter(Publication.user_id != current_user.id).all()
    publications = [pub.filename_photo for pub in publications]  # Выбираем оттуда только путь к файлу

    # Перемещиваем случайным образом и обрезаем список до заданной длины (по умолчанию 99)
    publications = random_list(publications)

    return render_template('explore.html', title='Публикации', publications=publications)


@app.route('/direct')
def direct():
    return render_template('direct.html', title='Cообщения')


@app.route('/home')
def home():
    return render_template('home.html', title='Home')


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
