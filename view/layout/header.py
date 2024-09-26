from dash import html
import dash_bootstrap_components as dbc

def header():
    return dbc.Container(
        [
            html.H1("Header", className="display-4"),
            html.Hr(),
        ],
        fluid=True,
      
    )