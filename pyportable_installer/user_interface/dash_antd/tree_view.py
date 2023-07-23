import typing as t

import feffery_antd_components as fac
from dash import ctx
from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from lk_utils import fs

from ._dash_app import app
from .demo_data import fake
from .tree_model import T as T0
from .tree_model import get_tree_model


class T:
    CheckedKeys = t.List[str]
    SelectedKeys = t.List[str]  # the list length is always 1
    TreeData = T0.TreeModel


def main(dir_i: str, dir_o: str) -> html.Div:
    return html.Div(  # root
        [
            html.Div(
                [
                    _tree_view(
                        'tree0',
                        dir_i,
                        # gen_demo_data(count_max=10, depth_max=5),
                        get_tree_model(dir_i),
                        checkable=True,
                    ),
                    _tree_view(
                        'tree1',
                        dir_o,
                        [
                            {
                                'title': fs.dirname(dir_o),
                                'key': 'root',
                                'children': [],
                            }
                        ],
                        checkable=False,
                    ),
                ],
                className='d-flex',
            )
        ],
        className='container-lg clearfix',
    )


def _tree_view(
    id: str, root: str, data: T.TreeData, checkable: bool
) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    dcc.Input(
                        root,
                        placeholder='Drop a folder here to load the tree',
                        className='form-control width-full',
                    ),
                    html.Button(
                        'Refresh tree',
                        id=f'{id}-test_btn',
                        className='btn mt-2',
                    ),
                    html.Div(  # wrapper
                        [
                            fac.AntdTree(
                                id=id,
                                checkable=checkable,
                                expandedKeys=['root'],
                                # defaultExpandAll=True,
                                treeData=data,
                                treeDataMode='flat',
                            )
                        ],
                        style={
                            'overflow': 'auto',
                            'height': '400px',
                            'max-height': '400px',
                        },
                    ),
                ],
                className=(
                    'd-flex '
                    'flex-column '
                    'justify-content-center '
                    'align-items-center'
                ),
            )
        ],
        className='flex-1 p-4',
    )


@app.callback(
    Output('tree1', 'treeData'),
    Input('tree0', 'checkedKeys'),
    State('tree0', 'treeData'),
    State('tree1', 'treeData'),
)
def _on_check(
    keys: T.CheckedKeys, data0: T.TreeData, data1: T.TreeData
) -> t.List[dict]:
    print(keys, ':vl')
    global _checked_keys
    _checked_keys = keys
    
    if keys:
        
        def recurse(node0, node1):
            for item in node0:
                if item['key'] in keys:
                    node1.append(item)
                    continue
                if item['children']:
                    recurse(item['children'], sublist := [])
                    if sublist:
                        node1.append(
                            {
                                'title': item['title'],
                                'key': item['key'],
                                'children': sublist,
                            }
                        )
        
        data1[0]['children'].clear()
        recurse(data0[0]['children'], data1[0]['children'])
    else:
        data1[0]['children'].clear()
    return data1


@app.callback(
    Output('tree0', 'selectedKeys'),
    Output('tree1', 'selectedKeys'),
    Input('tree0', 'selectedKeys'),
    Input('tree1', 'selectedKeys'),
)
def _on_select(
    sel0: T.SelectedKeys, sel1: T.SelectedKeys
) -> t.Tuple[T.SelectedKeys, T.SelectedKeys]:
    if sel0 is None and sel1 is None:
        raise PreventUpdate
    # assert len(sel0) <= 1 and len(sel1) <= 1
    print(ctx.triggered)
    out = ctx.triggered[0]['value']
    print(sel0, sel1, out)
    return out, out


_checked_keys: T.CheckedKeys = []


@app.callback(
    Output('tree0', 'treeData'),
    Output('tree0', 'checkedKeys'),
    Input('tree0-test_btn', 'n_clicks'),
    State('tree0', 'treeData'),
)
def _refresh_tree(
    n: t.Optional[int], data: T.TreeData
) -> t.Tuple[T.TreeData, T.CheckedKeys]:
    if not n:
        return data, _checked_keys
    
    def recurse(node: t.List[dict]):
        for item in node:
            item['title'] = fake.name()
            if item['children']:
                recurse(item['children'])
    
    recurse(data)
    return data, _checked_keys
