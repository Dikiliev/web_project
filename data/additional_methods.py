from random import shuffle
from PIL import Image
import datetime


def is_latin(text):
    latin = 'abcdefghijklmnopqrstuvwxyz._0123456789'
    for letter in text:
        if letter not in latin:
            return False
    return True


def image_size(image, filename, size=(1600, 1600)):

    with open('static/' + filename, 'wb') as file:
        file.write(image.read())
        file.close()

    from PIL import Image

    img = Image.open('static/' + filename)

    x, y = img.size
    remainder = abs(x - y) // 2

    if x > y:
        area = (remainder, 0, x - remainder, y)

    else:
        area = (0, remainder, x, y - remainder)

    img = img.crop(area)
    img = img.resize((size[0], size[1]), Image.ANTIALIAS)
    img.save('static/' + filename)


def random_list(list_, len_=99):
    if not list_:
        return False
    list_ = list_[:len_]
    shuffle(list_)
    return list_


def get_date(date):
    period = datetime.datetime.now() - date
    result = ''
    if period.days > 7:
        result = date.date
    elif period.days > 1:
        result = f'{period.days} дней назад'
    elif period.days == 1:
        result = f'День назад'
    elif period.seconds // 3600 > 1:
        result = f'{period.seconds // 3600} часов назад'
    elif period.seconds // 3600 == 1:
        result = f'Час назад'
    elif period.seconds // 60 > 1:
        result = f'{period.seconds // 60} минут назад'
    elif period.seconds > 1:
        result = f'{period.seconds} секунды назад'
    else:
        result = f'Только что'

    return result.upper()


class Theme:
    css_file = 'css/red_dark.css'
    background_color = '#1A1A1D'
    color = '#dc3545'
    style = 'danger'
    style_btn = 'dark'
    icon_name = ''

    def __init__(self, css_file, background_color, color, style, style_btn, icon_name=''):
        self.css_file = css_file
        self.background_color = background_color
        self.color = color
        self.style = style
        self.style_btn = style_btn
        self.icon_name = icon_name


ICONS = ['circle.png', 'close.png', 'explore_false.png', 'explore_true.png', 'home_false.png', ]
RED_DARK_THEME = Theme('css/red_dark.css', '#1A1A1D', '#dc3545', 'danger', 'dark')
RED_LIGHT_THEME = Theme('css/red_light.css', '#eeeeee', '#dc3545', 'danger', 'light')

GREEN_DARK_THEME = Theme('css/green_dark.css', '#1A1A1D', '#198754', 'success', 'dark', 'green_')
GREEN_LIGHT_THEME = Theme('css/green_light.css', '#eeeeee', '#198754', 'success', 'light', 'green_')

themes = [RED_DARK_THEME, RED_LIGHT_THEME, GREEN_DARK_THEME, GREEN_LIGHT_THEME]


def next_theme(current_theme):
    index = themes.index(current_theme)
    index = (index + 1) % len(themes)
    return themes[index]
