"""
****** Important! *******
If you run this app locally, un-comment line 127 to add the theme change components to the layout
"""

from dash import Dash
import dash_bootstrap_components as dbc
from view.layout.layout import create_layout

# stylesheet with the .dbc class to style  dcc, DataTable and AG Grid components with a Bootstrap theme
# 1- initializing the app
# 2- loading css 
# 3- calling bootstrap
# 4- linking fontawesome
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = Dash(__name__, use_pages=True, pages_folder='view/pages', suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css])


app.layout = create_layout('kd')

if __name__ == "__main__":
    app.run_server(debug=True)