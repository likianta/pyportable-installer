import re
from textwrap import dedent


def analyse_docstring(docstring: str) -> dict:
    """
    example:
        docstring:
            ~ run daemon in background. (you may register an account first.)
            ~
            ~ args:
            ~     username:
            ~     password:
            ~
            ~ options:
            ~     --debug: debug mode
        analysis result:
            {
                'desc': 'run daemon in ...',
                'args': {
                    'username': 'username',
                    'password': 'password',
                },
                'options': {
                    '--debug': 'debug mode',
                }
            }
    """
    result = {
        'desc'   : '',
        'args'   : {},
        'options': {},
    }
    
    # sanitize docstring
    if len(docstring) >= 2 and (docstring[0] == ' ' and docstring[1] != ' '):
        docstring = '   ' + docstring
    docstring = dedent(docstring).strip()
    
    # walk through lines
    scope = 'root'  # root, args, options, other
    last_key = ''
    
    for line in docstring.split('\n'):
        line = line.rstrip()
        if not line:
            continue
    
        if line.startswith('args:'):
            scope = 'args'
            continue
        elif line.startswith('options:'):
            scope = 'options'
            continue
        else:
            if scope == 'root':
                pass
            elif scope == 'other':
                continue
            elif not line.startswith('    '):
                scope = 'other'
                continue
        # lk.logt('[D3125]', line, scope)
        
        if scope == 'root':
            result['desc'] += _pretty_line_feed(line)
        elif scope == 'args' or scope == 'options':
            node = result[scope]  # dict[str field, str text]
            line = line[4:]  # dedent 4 spaces
            if m := re.compile(r'^([-\w]+): ?(.*)').match(line):
                field = m.group(1)
                text = m.group(2)
                node[field] = text
                last_key = field
                continue
            else:
                line = line[4:]
                node[last_key] += _pretty_line_feed(line)
    
    # sanitize result
    result['desc'] = _sanitize_text(result['desc'])
    for scope in ('args', 'options'):
        for field, text in result[scope].items():
            result[scope][field] = _sanitize_text(text)

    # lk.logp(result, h='parent')
    
    return result


def _pretty_line_feed(line: str) -> str:
    def is_soft_wrap_line(line: str) -> bool:
        if len(line) >= 2 and (line[0] == ' ' and line[1] != ' '):
            return True
        else:
            return False
    
    if is_soft_wrap_line(line):
        return ' ' + line.strip()
    else:
        return '\n' + line


def _sanitize_text(text: str) -> str:
    """
    note:
        in rich-click, single newline (\n) will be removed, double newlines
        (\n\n) will be preserved as one newline.
    """
    return text.strip().replace('\n', '\n\n')
