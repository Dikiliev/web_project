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
    shuffle(list_)
    return list_
