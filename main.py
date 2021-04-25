from flask import Flask, render_template, redirect, request, make_response, session, abort, url_for
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.publications import Publication
from data.notifications import Notification
from forms.users import RegisterForm, LoginForm, EditProfileForm, ProfileForm
from forms.publications import AddPublicationForm, ShowPublicationForm, EditPublicationForm
from forms.search import SearchForm

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

# Описано additional_methods.py
from data.additional_methods import is_latin, image_size, random_list, next_theme, themes, get_date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def get_theme():    # Возвращает текушую тему
    return themes[int(request.cookies.get("theme_index", 0))]


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect('/home')
    return redirect('/login')


@app.route('/profile/<name>', methods=['GET', 'POST'])
def profile(name):    # Страница профиля
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()

    if user is None:    # Если пользователя не существует
        return render_template('profile.html', title='profile', theme=get_theme(), user_data=False)

    current_user.load_data()    # Загрузка дополнительных данных пользователя
    curr_user_data = current_user.other_data

    user.__init__()    # Загрузка дополнительных данных данного пользователя
    user_data = user.other_data

    # Берем публикации данного пользователся и сортируем их по дате загрузки
    publications = db_sess.query(Publication).filter(Publication.user_id == user.id).all()
    publications = sorted(publications, key=lambda p: p.created_date, reverse=True)
    # Берем оттуда только id и путь к файлу
    publications = [[pub.id, pub.filename_photo] for pub in publications]

    form = ProfileForm()
    if form.validate_on_submit():
        # Если нажата кнопка отписатся
        if user.id in current_user.other_data['subscriptions']:
            # Удаление пользователя из подписок и удаление текущего пользовтеля из его подписчиков
            current_user.other_data['subscriptions'].remove(user.id)
            user.other_data['followers'].remove(current_user.id)

            # Удаление уведомления
            notification = db_sess.query(Notification).filter(Notification.publication_id == -1,
                                                              Notification.sender_id == current_user.id,
                                                              Notification.recipient_id == user.id).first()
            if notification is not None:
                db_sess.delete(notification)
                db_sess.commit()
        # Инача (нажата кнопка подписатся)
        else:
            # Добавление пользователя в подписки и добавление текущего пользователся в его подписки
            current_user.other_data['subscriptions'].append(user.id)
            user.other_data['followers'].append(current_user.id)

            # Добавление уведомления
            notification = Notification()
            notification.publication_id = -1
            notification.sender_id = current_user.id
            notification.recipient_id = user.id
            db_sess.add(notification)
            db_sess.commit()

        # Сохрание данных обэих пользователей
        user.save_data()
        current_user.save_data()

    return render_template('profile.html', title='profile', theme=get_theme(), form=form, user=user,
                           user_data=user_data, curr_user_data=curr_user_data, pubs=publications)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():     # Редактирование дыннх пользоветеля
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

            # Сохрание фотографии
            image_size(request.files['file'], photo_name)
            user.filename_photo = photo_name

        db_sess.commit()
        # Для обновления данных current_user
        load_user(user.id)

        return redirect(f'/profile/{user.name}')

    form.name.data = current_user.name
    form.full_name.data = current_user.full_name
    form.about.data = current_user.about
    form.email.data = current_user.email
    form.phone.data = current_user.phone

    current_user.load_data()
    user_data = current_user.other_data

    return render_template('edit_profile.html', title='Изменить профиль', theme=get_theme(), form=form, user_data=user_data)


@app.route('/search', methods=['GET', 'POST'])
def search_user():      # Поиск других пользователй
    form = SearchForm()
    if form.validate_on_submit():
        name = form.name.data  # Введенная пользователем имя (часть имени)
        db_sess = db_session.create_session()

        # Пользаветели чьи имена начинаются на name
        users = db_sess.query(User).filter((User.name.like(f'{name}%')) | (User.full_name.like(f'{name}%'))).all()
        # Добавление пользаветелей чьич именах есть name
        users += db_sess.query(User).filter(User.id.notin_([user.id for user in users]),
                                            (User.name.like(f'%{name}%')) | (User.full_name.like(f'%{name}%'))).all()

        return render_template('search.html', title='Поиск', theme=get_theme(), form=form, users=users)

    return render_template('search.html', title='Поиск', theme=get_theme(), form=form)


@app.route('/add_publication', methods=['GET', 'POST'])
def add_publication():  # Добавление публикации
    form = AddPublicationForm()

    if form.submit_view.data or form.submit.data:
        current_user.load_data()  # Загрузка дополнительных данных пользователя
        # Создание пути к файлу
        photo_name = f'user_data/publications/id_{current_user.id}_pub_{len(current_user.other_data["publications"]) + 1}.png'

        # Сохранение фотографии
        if request.files['file']:

            # Если загружены неправильные данные
            if form.file.data.filename.split('.')[-1] not in ('png', 'jpg'):
                print('error')
                return render_template('add_publication.html', title='Добавить новость', theme=get_theme(),
                                       form=form, message='Загрузите фотографию формата .png или .jpg')

            # Сохранение фотографии
            image_size(request.files['file'], photo_name)

        # Если нажата кнопка "Опубликовать"
        if form.submit.data:
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
            return render_template('add_publication.html', title='add_publication', theme=get_theme(), form=form, photo_name=photo_name)
    return render_template('add_publication.html', title='Добавить новость', theme=get_theme(), form=form)


@app.route('/edit_publication/<id_>', methods=['GET', 'POST'])
def edit_publication(id_):  # Редактировине публикации
    form = EditPublicationForm()

    db_sess = db_session.create_session()
    publication = db_sess.query(Publication).filter(Publication.id == int(id_)).first()

    if form.submit.data:

        # Редактирование...
        publication.about = form.about.data
        db_sess.commit()

        return redirect(f'/profile/{current_user.name}')

    if form.submit_delete.data:

        # Удаление...
        db_sess.delete(publication)
        db_sess.commit()

        return redirect(f'/profile/{current_user.name}')

    form.about.data = publication.about
    photo_name = publication.filename_photo

    return render_template('edit_publication.html', title='Редактировать', theme=get_theme(), form=form, photo_name=photo_name)


@app.route('/show_publication/<id_>', methods=['GET', 'POST'])
def show_publication(id_):  # Показ публикации
    form = ShowPublicationForm()
    db_sess = db_session.create_session()

    # Берем публикацию и загружаем ее дополнительные данные
    publication = db_sess.query(Publication).filter(Publication.id == int(id_)).first()
    publication.__init__()
    current_user.load_data()

    user = db_sess.query(User).filter(User.id == publication.user_id).first()
    date = get_date(publication.created_date)

    if form.validate_on_submit():
        if form.like_submit.data:
            if publication.id in current_user.other_data['likes']:
                # Удаление лайка файлах пользователя и публикации
                publication.other_data['likes'].remove(current_user.id)
                current_user.other_data['likes'].remove(publication.id)

                # Удаление уведомления
                notification = db_sess.query(Notification).filter(Notification.publication_id == publication.id,
                                                                  Notification.sender_id == current_user.id,
                                                                  Notification.recipient_id == user.id).first()
                if notification is not None:
                    db_sess.delete(notification)
            else:
                # Добавление лайка файлах пользователя и публикации
                publication.other_data['likes'].append(current_user.id)
                current_user.other_data['likes'].append(publication.id)

                # Добавление уведомления
                notification = Notification()
                notification.publication_id = publication.id
                notification.sender_id = current_user.id
                notification.recipient_id = user.id
                db_sess.add(notification)
                db_sess.commit()

            current_user.save_data()
            publication.save_data()

    return render_template('publication.html', title='Публикация', theme=get_theme(),
                           form=form, user=user, publication=publication, date=date)


@app.route('/view_users/<type_>/<id_>', methods=['GET', 'POST'])
def view_users(type_, id_):     # Простомт подписчиков/подписок/лайкнувших
    db_sess = db_session.create_session()
    current_user.load_data()

    users = []
    title_ = ''
    # Думаю тут понятно...
    if type_ == 'likes':
        # Публикация чьи лайкнувших мы берем
        publication = db_sess.query(Publication).filter(Publication.id == id_).first()
        publication.load_data()
        users = db_sess.query(User).filter(User.id.in_(publication.other_data['likes'])).all()
        title_ = 'Отметки "Нравится"'
        url_closing = f'/show_publication/{publication.id}'
    else:
        user = db_sess.query(User).filter(User.id == id_).first()
        user.load_data()
        url_closing = f'/profile/{user.name}'

        if type_ == 'subscribers':
            title_ = 'Подписки'
            users = db_sess.query(User).filter(User.id.in_(user.other_data['subscriptions'])).all()

        elif type_ == 'followers':
            title_ = 'Подписчики'
            users = db_sess.query(User).filter(User.id.in_(user.other_data['followers'])).all()

    return render_template('view_users.html', title=type_, theme=get_theme(), users=users, title_=title_, url_closing=url_closing)


@app.route('/notification')
def show_notification():    # Страница уведомлении
    db_sess = db_session.create_session()

    notifications_ = db_sess.query(Notification).filter(Notification.recipient_id == current_user.id).all()
    notifications_ = sorted(notifications_, key=lambda n: n.created_date, reverse=True)     # Сортировка по дате

    notifications = []

    for notification in notifications_:
        # Отправитель
        user = db_sess.query(User).filter(User.id == notification.sender_id).first()
        if notification.publication_id == -1:
            publication = False
        else:
            publication = db_sess.query(Publication).filter(Publication.id == notification.publication_id).first()

        date = get_date(notification.created_date)      # Возвращает дату/период

        notifications.append([user, notification, publication, date])

    return render_template('notification.html', title='Уведомления', theme=get_theme(), notifications=notifications)


@app.route('/explore')
def explore():
    db_sess = db_session.create_session()
    # Достаем все публикации кроме публкации текущего пользователя
    publications = db_sess.query(Publication).filter(Publication.user_id != current_user.id).all()
    publications = [[pub.id, pub.filename_photo] for pub in publications]  # Выбираем оттуда только id и путь к файлу

    # Перемещиваем случайным образом и обрезаем список до заданной длины (по умолчанию 99)
    publications = random_list(publications)

    return render_template('explore.html', title='Публикации', theme=get_theme(), publications=publications)


@app.route('/home')
def home():     # Домашняя страница, тут показываются публикации только тех людей, на которых подписан пользователь
    db_sess = db_session.create_session()
    current_user.load_data()
    # Публикации опубликованные пользователями на которых подписан пользователь
    publications = db_sess.query(Publication).filter(
        Publication.user_id.in_((current_user.other_data['subscriptions']))).all()

    pubs = []
    for pub in publications:
        user = db_sess.query(User).filter(User.id == pub.user_id).first()   # Пользователь который опуликовал...
        date = get_date(pub.created_date)   # Дата...
        pubs.append([pub, user, date])   # ...

    return render_template('home.html', title='Home', theme=get_theme(), pubs=pubs)


@app.route('/register', methods=['GET', 'POST'])
def register():   # С урока...
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, title='Регистрация', theme=get_theme(), message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, title='Регистрация', theme=get_theme(),
                                   message='Почта уже зарегистрирована')

        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', form=form, title='Регистрация', theme=get_theme(),
                                   message='Имя пользователя занято')

        if not is_latin(form.name.data):
            return render_template('register.html', form=form, title='Регистрация', theme=get_theme(),
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
    return render_template('register.html', form=form, title='Регистрация', theme=get_theme())


@app.route('/login', methods=['GET', 'POST'])
def login():    # Тоже с урока...
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            (User.name == form.name_or_email.data) | (User.email == form.name_or_email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', title='Авторизация', form=form, theme=get_theme(),
                               message='Неправильные данные для авторизации')
    return render_template('login.html', title='Авторизация', form=form, theme=get_theme())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/change_theme')
def change_theme():   # Меняет тему и помещает ее индекс в куки
    theme_index = int(request.cookies.get("theme_index", 0))
    theme_index = (theme_index + 1) % len(themes)

    res = make_response(redirect('/home'))
    res.set_cookie("theme_index", str(theme_index),
                   max_age=60 * 60 * 24 * 365 * 2)
    return res


def main():
    db_session.global_init('db/blogs.sqlite')
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
