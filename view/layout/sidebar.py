import dash_bootstrap_components as dbc
from dash import html
SIDEBAR_STYLE = {
    "width": "100%",
    "backgroundColor": "#f8f9fa",
}
# Sidebar component with NavLinks for navigating between pages
def sidebar():
    return dbc.Container(
        [
            html.H2("FINNSIP", className="display-4"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Projects", href="/", active="exact"),
                    dbc.NavLink("Inventory", href="/inventory", active="exact"),
                    dbc.NavLink("Page 2", href="/page-2", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )
