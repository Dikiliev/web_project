from random import shuffle


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


class Theme:
    css_file = 'css/red_dark.css'
    background_color = '#1A1A1D'
    color = '#dc3545'
    style = 'danger'
    style_btn = 'dark'

    def __init__(self, css_file, background_color, color, style, style_btn):
        self.css_file = css_file
        self.background_color = background_color
        self.color = color
        self.style = style
        self.style_btn = style_btn


RED_DARK_THEME = Theme('css/red_dark.css', '#1A1A1D', '#dc3545', 'danger', 'dark')
RED_LIGHT_THEME = Theme('css/red_light.css', '#eeeeee', '#dc3545', 'danger', 'light')

themes = [RED_DARK_THEME, RED_LIGHT_THEME]


def next_theme(current_theme):
    index = themes.index(current_theme)
    index = (index + 1) % len(themes)
    return themes[index]
