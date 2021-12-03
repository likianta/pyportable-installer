# noinspection PyMethodMayBeStatic
class Commander:
    
    def say_hello(self):
        print("Hello")
    
    def say_anything(self, word):
        print(word)


def main():
    import fire
    fire.Fire(Commander())
