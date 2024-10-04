# /pages/page2.py
from dash import html, register_page, callback, dcc, callback_context
import dash as dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row, Col, Label, Input
from datetime import datetime
import pandas as pd
from data.data import get_inventory_instruments_number, add_to_table
register_page(__name__, path="/add-instrument", name="Add instrument")  # Register a page at /add-instrument


layout = html.Div([
    dcc.Interval(id='interval', interval=1, n_intervals=0, max_intervals=1),
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
                                    dbc.Label("Instrument", html_for="instrument-dropdown-inventory", width=6),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id='instrument-dropdown-inventory',
                                            options=[
                                                
                                            ],
                                            value=None,  # Default value
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
                                    dbc.Label("ID", html_for="instrument-id", width=6),
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
                                dbc.Col(dbc.Button("Submit", id="submit-form-inventory", n_clicks=0, color="primary", disabled=True), width="auto"),
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
    dash.Output('instrument-dropdown-inventory', 'options'),
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
    
    dash.Output('submit-form-inventory', 'disabled'),
    [
        dash.Input('instrument-dropdown-inventory', 'value'),   
        dash.Input('instrument-name', 'value'),
        dash.Input('instrument-id', 'value'),
        dash.Input('instrument-number', 'value'),
    ],
)
def check_if_required_inputs_are_filledIn(selected_option, name, id, number):
    if not selected_option or number == 0: 
        return True
    if selected_option == "New" and (not name or not id or number < 1):
        return True
    return False

@callback(
    [
        dash.Output('instrument-name-container', 'style'),
        dash.Output('instrument-id-container', 'style')
    ],
    dash.Input('instrument-dropdown-inventory', 'value')
)
def toggle_name_and_id(selected_option):
    if selected_option == "New":
        return {}, {}  # returning for both elements. removes the style (display none will be removed)
    else:
        return {'display': 'none'} , {'display': 'none'} 

@callback(
    
    dash.Output('toast-store', 'data', allow_duplicate=True), 
    
    dash.Input('submit-form-inventory', 'n_clicks'),
    dash.State('instrument-dropdown-inventory', 'value'),   
    dash.State('instrument-name', 'value'),
    dash.State('instrument-id', 'value'),
    dash.State('instrument-number', 'value'),
    dash.State('owner', 'value'), 
    dash.State('storage-location', 'value'),
   
    prevent_initial_call=True
)
def submit_form_inventory(n_clicks, selected_option, name_input, id_input, number, owner, 
    location):
    if n_clicks is None or n_clicks == 0 :
        raise PreventUpdate
    else:
        toast = {
            'is_open': False, 
            'message': '', 
            'header': 'Success', 
            'icon': 'success'
        }
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

        response = add_to_table(inventory_row, "Inventory")
        if response["status"] == "success":
            # Show success message
            toast = {
                'is_open': True, 
                'message': 'Inventory created successfully!', 
                'header': 'Success', 
                'icon': 'success'
            }
        else:
            # Handle the error
            toast = { 
                'is_open': True, 
                'message': 'There is something wrong!', 
                'header': 'Failure', 
                'icon': 'failure'
            }
            
        return toast
   