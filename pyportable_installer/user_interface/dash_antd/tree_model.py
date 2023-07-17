import typing as t

from lk_utils import fs


class T:
    TreeModel = t.List[
        t.TypedDict(
            'TreeData',
            {
                'title': str,
                'key': str,
                'children': t.Optional[t.List['TreeData']],
            },
        )
    ]


def get_tree_model(root: str) -> T.TreeModel:
    """
    TODO: respect `.gitignore` rules.
    """
    _depth = 0
    _index = 0

    def recurse(node: dict, path: str) -> dict:
        nonlocal _depth, _index
        _depth += 1
        if _depth > 20:
            print(':v3', 'too deep (>20), stop recusion!')
            return node

        for i, d in enumerate(fs.find_dirs(path)):
            if i > 100:
                print(':v3', 'too many folders (>100), stop recusion!')
                return node
            _index += 1
            node['children'].append(
                subnode := {'key': str(_index), 'title': d.name, 'children': []}
            )
            recurse(subnode, d.path)

        for i, f in enumerate(fs.find_files(path)):
            if i > 1000:
                print(':v3', 'too many files (>1000), stop recusion!')
                return node
            _index += 1
            node['children'].append(
                {'key': str(_index), 'title': f.name, 'children': None}
            )

        _depth -= 1
        return node

    tree = recurse(
        {'key': 'source_root', 'title': root, 'children': []}, root
    )
    return [tree]
