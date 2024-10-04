import dash_bootstrap_components as dbc
from dash import html
SIDEBAR_STYLE = {
    "width": "100%",
    "backgroundColor": "#f8f9fa",
    "height": "100%"
}
# Sidebar component with NavLinks for navigating between pages
def sidebar():
    return dbc.Container(
        [
            html.Div([
                html.Img(src='/assets/Logo_University_of_Helsinki_fi.png', style={"width":"150px", "width": "150px", "padding":"20px"}),
                html.H2("FINNSIP", className="display-4"),
            ],className="d-flex flex-column justify-content-center align-items-center"),
            html.Hr(style={"width": "100%"}),
            dbc.Nav(
                [
                    dbc.NavLink("Overview", href="/", active="exact"),
                    dbc.NavLink("Projects", href="/project", active="exact"),
                    dbc.NavLink("Inventory", href="/inventory", active="exact"),
                    dbc.NavLink("Repair", href="/repair", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )
