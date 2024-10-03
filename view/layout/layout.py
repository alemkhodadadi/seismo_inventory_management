from dash import dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from view.layout.sidebar import sidebar 
from view.layout.content import content
from view.utils import global_toast

def create_layout(df):
    layout = dbc.Container(
        [
            dcc.Location(id="url"), 
            dbc.Row(    
                [
                    dbc.Input(id='dummy-input', value="dummy", style={"display": "none"}),
                    dbc.Col(
                        sidebar(), 
                        width=2, 
                    ),
                    dbc.Col(
                        content(), 
                        width=10, 
                    )    
                ],
                justify="between",
                style={"display":"flex", "flex": "1"}
            ),
            global_toast(),
            dcc.Store(id='toast-store', data={'is_open': False, 'message': '', 'header': '', 'icon': ''}),

        ],
        fluid=True,
        className="dbc dbc-ag-grid ",
        style={"height":"100vh", "display": "flex"}
    )
    return layout



@callback(
    Output('global-toast', 'is_open'),
    Output('global-toast', 'children'),
    Output('global-toast', 'header'),
    Output('global-toast', 'icon'),
    [Input('toast-store', 'data')]  # Store the toast state here
)
def update_toast(toast_data):
    if toast_data['is_open']:
        return True, toast_data['message'], toast_data['header'], toast_data['icon']
    return False, "", "", ""