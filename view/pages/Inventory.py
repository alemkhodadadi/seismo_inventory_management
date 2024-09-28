from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_inventory
import pandas as pd
import dash_ag_grid as dag
from view.utils import create_gantt

register_page(__name__, path="/inventory")  # Register a page at /page-2

def layout():
    inventory = get_inventory()
    return html.Div(
        [
            html.Div(
                [
                    html.Hr(),
                    html.Div([
                        dcc.Link(
                            dbc.Button(
                                "Add Instrument", 
                                color="primary",  # Bootstrap button style
                                className="me-1"
                            ),
                            href="/add-instrument"  # Set the path for the navigation
                        ),
                        dbc.Button(
                            "Update Table",
                            id="update-table-button",
                            color="dark",  # Bootstrap button style
                            className="me-1",
                            disabled=True,
                            n_clicks=0
                        ),
                    ]),
                    html.Hr(),
                ]
            ),
            dbc.Row([
                dag.AgGrid(
                    id="table-projects-editable",
                    rowData=inventory.to_dict("records"),
                    columnDefs=[
                        {"field": i} for i in inventory.columns if i not in ['Number_sum']
                    ],
                    defaultColDef={"filter": True, 'editable': True},
                    dashGridOptions={"pagination": True},
                    style={"minHeight":"800px"},
                ),
                dcc.Store(id='table-projects-editable-changes', data=[]),
            ])
        ]
    )