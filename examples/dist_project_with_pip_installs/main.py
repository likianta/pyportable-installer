from lk_logger import lk

a = 1
b = 2
c = 3

lk.loga(a, b, c)
lk.loga(a + 1, b * 2, c / 3)
lk.loga((a, b), {c: b + a}, f'''
    a, b, c = {a} , {b}, {c} ''')

input('over')
