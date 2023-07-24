from captcha.image import ImageCaptcha
from random import choices
import string
from os import remove


def captca(user_id: int):
    patterns = string.ascii_uppercase + string.digits
    rand = ''.join(choices(patterns, k=5))
    captha = ImageCaptcha(width=300, height=100).write(
        rand, f'captcha{user_id}.png')
    return rand


def delete_captcha(user_id: int):
    remove(f'captcha{user_id}.png')
    return f'Captcha пользователя {user_id} удалена'


if __name__ == '__main__':
    captca(11)