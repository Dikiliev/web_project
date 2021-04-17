def is_latin(text):
    latin = 'abcdefghijklmnopqrstuvwxyz._0123456789'
    for letter in text:
        if letter not in latin:
            return False
    return True
