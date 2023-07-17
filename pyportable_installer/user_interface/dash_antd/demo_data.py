from random import choice
from random import randint

from faker import Faker

fake = Faker()
_id = 0


def gen_demo_data(count_max: int = 1, depth_max: int = 3):
    out = []
    
    count = 0
    depth = 0
    
    def recurse(node):
        global _id
        nonlocal count, depth
        if count > count_max:
            return
        depth += 1
        if depth > depth_max:
            depth -= 1
            return
        
        for i in range(randint(10, 50)):
            count += 1
            if count > count_max:
                return
            is_file = choice((True, False))
            _id += 1
            node.append({
                'title'   : fake.name(),
                'key'     : str(_id),
                'children': is_file and None or (sublist := [])
            })
            if not is_file:
                recurse(sublist)  # noqa
    
    recurse(out)
    
    print(out, ':vlp')
    return out
