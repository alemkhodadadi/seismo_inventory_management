import dash_bootstrap_components as dbc
from dash import page_container, html, callback
from dash.dependencies import Input, Output
import dash 

CONTENT_TOP_STYLE = {
    "padding": "4rem",
    "paddingBottom": "1rem",
    "position": "sticky",
    "top": "0px",
    "zIndex": "99", 
    "backgroundColor": "white",
    "boxShadow": "rgba(0, 0, 0, 0.25) 0px 2px 10px 0px",
}

CONTENT_BOTTOM_STYLE = {
    "paddingRight": "3rem",
    "paddingLeft": "3rem"
}

CONTENT_STYLE = {
    "overflowY": "scroll", 
    "overflowX": "hidden", 
    "maxHeight": "100vh",
}
# Content component with dynamic page container
def content():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H1(id='page-title'), 
                        width=12,
                    ),
                ],
                style=CONTENT_TOP_STYLE
            ),
            
            dbc.Row(
                [
                    page_container,  # This renders the page content based on the route
                ],
                style=CONTENT_BOTTOM_STYLE
            )
            
        ],
        style=CONTENT_STYLE
    )

# Callback to update the page title dynamically
@callback(
    Output('page-title', 'children'),
    [Input('url', 'pathname')]  # Getting the current page URL
)
def update_page_title(pathname):
    # Get the page title from dash.page_registry based on the current pathname
    if pathname in dash.page_registry:
        return dash.page_registry[pathname]['name']
    return "Home"  # Default page title if no page is found
