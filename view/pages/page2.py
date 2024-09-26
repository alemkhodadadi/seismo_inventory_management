# /pages/page2.py
from dash import html, register_page

register_page(__name__, path="/page-2")  # Register a page at /page-2

layout = html.Div([
    html.H2("Page 2"),
    html.P("This is the content for Page 2.")
])