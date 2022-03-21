import lk_logger
lk_logger.setup(show_varnames=True)

a = 1
b = 2
c = 3

print(a, b, c)
print(a + 1, b * 2, c / 3)
print((a, b), {c: b + a}, f'''
    a, b, c = {a} , {b}, {c} ''')

input('over')
