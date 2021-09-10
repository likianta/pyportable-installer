"""
Convert jpg, png, etc. to ico.

Requirements:
    pillow
    
BTW: You can find a convertion tool online, for example this site:
    https://www.easyicon.net/covert/
"""


def dialog():
    file_i = input('image: ')
    file_o = file_i.removesuffix('.png') + '.ico'
    main(file_i, file_o)


def main(file_i, file_o):
    try:
        # noinspection PyPackageRequirements
        from PIL import Image  # pip install pillow
    except (ModuleNotFoundError, ImportError) as e:
        print('Please install pillow library (pip install pillow)')
        raise e
    img = Image.open(file_i)
    img.save(file_o)
    img.close()


if __name__ == '__main__':
    dialog()
