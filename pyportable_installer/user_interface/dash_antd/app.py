from dash import dcc, html

from ._dash_app import app
from .tree_view import main as add_tree_view

print(':d')


def main(profile: dict) -> None:
    app.layout = html.Div(
        [
            # add primer cssˆ
            html.Link(
                rel='stylesheet',
                href='https://cdn.jsdelivr.net/npm/@primer/css@21.0.7/dist'
                     '/primer.min.css',
            ),
            _main_form(profile),
            add_tree_view(
                profile['build']['proj_root'],
                profile['build']['dist_root'],
            ),
        ],
        style={'padding': '2rem'},
    )
    app.run(port=3001, debug=True)


def _main_form(profile: dict) -> html.Div:
    layout = []
    
    def add_rows() -> None:
        for field, (value, placeholder) in {
            'Application name'   : (profile['app_name'], profile['app_name']),
            'Application version': (profile['app_version'], 'e.g. 0.1.0'),
        }.items():
            layout.append(add_label(field))
            layout.append(html.Div(
                [
                    dcc.Input(
                        value=value,
                        placeholder=placeholder,
                        className='form-control width-full',
                    )
                ]
            ))
    
    def add_label(label: str) -> html.Div:
        return html.Div(
            [html.Label(label + ': ')],
            className='d-flex',
            style={'justify-content': 'flex-end', 'align-items': 'center'},
        )
    
    add_rows()
    # add more labels
    layout.append(add_label('Assets (tree view)'))
    
    return html.Div(  # grid
        layout,
        style={
            'display'              : 'grid',
            'grid-template-columns': '160px 1fr',
            'grid-gap'             : '2px 1rem',
        },
    )
