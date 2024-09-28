# /pages/page2.py
from dash import html, register_page, callback, dcc
import dash as dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row, Col, Label, Input
from datetime import datetime
import pandas as pd
from data.data import get_inventory_instruments_number, add_inventory
register_page(__name__, path="/add-instrument", name="Add instrument")  # Register a page at /create-project


layout = html.Div([
    dcc.Interval(id='interval', interval=1, n_intervals=0, max_intervals=1),
    html.Div(id="kirekhar2",style={"display":"none"}),
    dbc.Form(
        dbc.Row(
            [
                dbc.Col(
                    children=(
                        [
                            html.H4("Add new instruments to inventory"),
                            html.Hr(),
                            dbc.Row(
                                [
                                    dbc.Label("Instrument", html_for="instrument-dropdown", width=6),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id='instrument-dropdown',
                                            options=[
                                                
                                            ],
                                            value='none',  # Default value
                                            placeholder="Select an option",
                                        ),
                                        width=6,
                                    )
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                id="instrument-name-container",
                                style={"display":"none"},
                                children=[
                                    dbc.Label("Name", html_for="instrument-name", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="instrument-name", placeholder="Name of new instrument"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                id="instrument-id-container",
                                style={"display":"none"},
                                children=[
                                    dbc.Label("Owner", html_for="instrument-id", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="instrument-id", placeholder="ID of new instrument"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Number", html_for="instrument-number", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="number", id="instrument-number", value=0
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Owner", html_for="owner", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="owner", placeholder="Owner"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Storage Location", html_for="storage-location", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="storage-location", placeholder="Storage Location"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            html.Hr(),
                            dbc.Row(
                                dbc.Col(dbc.Button("Submit", id="submit-form", n_clicks=0, color="primary"), width="auto"),
                                className="mb-3",
                            ),
                        ]
                    ),
                    width=8,
                    class_name="px-5 py-3"
                )
              
            ]
        )
    )
])

# Callback triggered automatically at app start
@callback(
    dash.Output('instrument-dropdown', 'options'),
    [dash.Input('interval', 'n_intervals')]
)
def update_content(n_intervals):
    if n_intervals == 0 or n_intervals == 1:
        instruments = get_inventory_instruments_number()  # Get the instruments DataFrame
        # Assuming instruments is a DataFrame with columns 'ID' and 'Number'
        options = [
            {'label': "Define New", 'value': "New"},
        ] + [
            {'label': f"{Name} ({ID})", 'value': f"{ID}"}
            for ID, Number, Name in zip(instruments['ID'], instruments['Number_sum'], instruments['Instrument name'])
        ]
        return options  # Return the dynamically created rows with input fields
    else:
        return [{'label': 'No instrument to show :('}]

@callback(
    [
        dash.Output('instrument-name-container', 'style'),
        dash.Output('instrument-id-container', 'style')
    ],
    dash.Input('instrument-dropdown', 'value')
)
def toggle_name_and_id(selected_option):
    print(selected_option)
    if selected_option == "New":
        return {}, {}  # returning for both elements. removes the style (display none will be removed)
    else:
        return {'display': 'none'} , {'display': 'none'} 

@callback(
    
    [dash.Output('kirekhar2', 'children')],  
    
    dash.Input('submit-form', 'n_clicks'),
    dash.State('instrument-dropdown', 'value'),   
    dash.State('instrument-name', 'value'),
    dash.State('instrument-id', 'value'),
    dash.State('instrument-number', 'value'),
    dash.State('owner', 'value'), 
    dash.State('storage-location', 'value'),
   
    prevent_initial_call=True
)
def submit_form(n_clicks, selected_option, name_input, id_input, number, owner, 
    location):
    print(n_clicks, selected_option, name_input, id_input, number, owner,location )
    instruments = get_inventory_instruments_number()
    if selected_option not in ["None", "New"]: 
        Name = instruments.loc[instruments["ID"] == selected_option, "Instrument name"].values[0]
        ID = selected_option
    if selected_option == "New":
        Name = name_input
        ID = id_input
    
    # Create the new inventory row
    inventory_row = {
        'Instrument name': Name,
        'ID': ID,
        'Number': number, 
        'Number_sum': number,
        'Owner': owner,
        'Storage location': location
    }

    response = add_inventory(inventory_row)
    return ''
    # if response["status"] == "success":
    #     # Show success message
    #     toast = {
    #         'is_open': True, 
    #         'message': 'Project created successfully!', 
    #         'header': 'Success', 
    #         'icon': 'success'
    #     }
    #     return toast
    # else:
    #     # Handle the error
    #     toast = {
    #         'is_open': True, 
    #         'message': 'There is something wrong!', 
    #         'header': 'Failure', 
    #         'icon': 'failure'
    #     }
    #     return toast

   