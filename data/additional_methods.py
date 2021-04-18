def is_latin(text):
    latin = 'abcdefghijklmnopqrstuvwxyz._0123456789'
    for letter in text:
        if letter not in latin:
            return False
    return True


def image_1600(image, name):

    with open(f'static/user_data/publications/{name}.png', 'wb') as file:
        file.write(image.read())
        file.close()

    from PIL import Image

    img = Image.open(f'static/user_data/publications/{name}.png')

    x, y = img.size
    remainder = abs(x - y) // 2

    if x > y:
        area = (remainder, 0, x - remainder, y)

    else:
        area = (0, remainder, x, y - remainder)

    img = img.crop(area)
    img = img.resize((1600, 1600), Image.ANTIALIAS)
    img.save(f'static/user_data/publications/{name}.png')
