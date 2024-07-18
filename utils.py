import string
import random

def randomString(limit):
    strings = string.ascii_letters
    f = ''
    for i in range(0, limit):
        k = random.randint(0, strings.__len__()) - 1
        f = f + strings[k]
    return f


