# /pages/page2.py
from dash import html, register_page, callback, dcc
import dash as dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row, Col, Label, Input
from datetime import datetime
import pandas as pd
from data.data import get_inventory_instruments_number, add_project
register_page(__name__, path="/add-project", name="Add project")  # Register a page at /create-project


layout = html.Div([
    dcc.Interval(id='interval', interval=1, n_intervals=0, max_intervals=1),
    html.Div(id="kirekhar",style={"display":"none"}),
    dbc.Form(
        dbc.Row(
            [
                dbc.Col(
                    children=(
                        [
                            html.H4("Fill in the project summary"),
                            html.Hr(),
                            dbc.Row(
                                [
                                    dbc.Label("Project name", html_for="project-name", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="project-name", placeholder="text"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Leading Institution", html_for="leading-institute", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="leading-institute", placeholder="text"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Partner institution(s)", html_for="partner-institute", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="partner-institute", placeholder="text"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Pickup date", html_for="pickup-date", width=6),
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id="pickup-date",
                                            month_format='MMMM Y',
                                            placeholder='MMMM Y',
                                            date=datetime.now().strftime("%Y-%m-%d")
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Return date", html_for="return-date", width=6),
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id="return-date",
                                            month_format='MMMM Y',
                                            placeholder='MMMM Y',
                                            date=datetime.now().strftime("%Y-%m-%d")
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
                    width=4,
                    class_name="px-5 py-3"
                ),
                dbc.Col(
                    children=(
                        [
                            html.H4("Project's Instruments"),
                            html.Hr(),
                            html.Div(
                                id="instruments-list",
                                children=[]                                
                            )
                        ]
                    ),
                    width=4,
                    class_name="px-5 py-3"
                ),
              
            ]
        )
    )
])

# Callback triggered automatically at app start
@callback(
    dash.Output('instruments-list', 'children'),
    [dash.Input('interval', 'n_intervals')]
)
def show_instruments_list(n_intervals):
    if n_intervals == 0 or n_intervals == 1:
        instruments = get_inventory_instruments_number()  # Get the instruments DataFrame
        # Assuming instruments is a DataFrame with columns 'ID' and 'Number'
        divs = [
            dbc.Row(
                [
                    dbc.Label(f"{ID}", html_for=f"{ID}", width=6),
                    dbc.Col(
                        dbc.Input(
                            type="number", id=f"{ID}", placeholder=f"{ID}", value=None
                        ),
                        width=6,
                    ),
                ],
                className="mb-3 justify-content-between align-items-center",
            )
            for ID, Number in zip(instruments['ID'], instruments['Number_sum'])
        ]


        return divs  # Return the dynamically created rows with input fields
    else:
        return "something is wrong in reading instruments" # In case nothing happens


@callback(
    
    dash.Output('toast-store', 'data', allow_duplicate=True),  # Second output
    
    dash.Input('submit-form', 'n_clicks'),
    dash.State('project-name', 'value'),   
    dash.State('leading-institute', 'value'),
    dash.State('partner-institute', 'value'),
    dash.State('pickup-date', 'date'),
    dash.State('return-date', 'date'), 
    dash.State('GSB3', 'value'),
    dash.State('GS-ONE5HZ', 'value'),
    dash.State('GSX3', 'value'),
    dash.State('LHR', 'value'),
    dash.State('LV', 'value'),
    dash.State('BN25', 'value'),
    dash.State('BN32', 'value'),
    dash.State('DTM48', 'value'),
    dash.State('DTM24', 'value'),
    dash.State('DC', 'value'),
    dash.State('BMS12', 'value'),
    dash.State('TOUGHBOOK', 'value'),
    dash.State('ZBOOK', 'value'),
    dash.State('IGU-16HR3C', 'value'),
    dash.State('SmartsoloCharger', 'value'),
    dash.State('SmartsoloRack', 'value'),
    dash.State('MAGNET', 'value'),
    dash.State('SDRX', 'value'),
    dash.State('MINIMUS', 'value'),
    dash.State('3ESPC', 'value'),
    dash.State('GNSS', 'value'),
    dash.State('CABLEBB', 'value'),
    dash.State('MASCOT', 'value'),
    dash.State('GELBATTERY', 'value'),
    dash.State('FORTIS', 'value'),
    prevent_initial_call=True
)
def submit_form(n_clicks, name, leading_inst, partner_inst, pickup, returnd, 
    gsb3, gs_one5hz, gsx3, lhr, lv, bn25, bn32, dtm48, dtm24, dc, 
    bms12, toughbook, zbook, igu_16hr3c, smartsoloCharger, 
    smartsoloRack, magnet, sdrx, minimus, espc3, gnss, cablebb, 
    mascot, gelbattery, fortis):
    # Convert the dates
    pickup_date = pd.Timestamp(pickup)
    return_date = pd.Timestamp(returnd)
    
    # Create the project data dictionary with instrument values
    project_data = {
        'Projects': name,
        'Leading Institution': leading_inst,
        'Partner institution(s)': partner_inst,
        'pickup_date': pickup_date,
        'return_date': return_date,
        'GSB3': gsb3,
        'GS-ONE5HZ': gs_one5hz,
        'GSX3': gsx3,
        'LHR': lhr,
        'LV': lv,
        'BN25': bn25,
        'BN32': bn32,
        'DTM48': dtm48,
        'DTM24': dtm24,
        'DC': dc,
        'BMS12': bms12,
        'TOUGHBOOK': toughbook,
        'ZBOOK': zbook,
        'IGU-16HR3C': igu_16hr3c,
        'SmartsoloCharger': smartsoloCharger,
        'SmartsoloRack': smartsoloRack,
        'MAGNET': magnet,
        'SDRX': sdrx,
        'MINIMUS': minimus,
        '3ESPC': espc3,
        'GNSS': gnss,
        'CABLEBB': cablebb,
        'MASCOT': mascot,
        'GELBATTERY': gelbattery,
        'FORTIS': fortis
    }

    response = add_project(project_data)
    if response["status"] == "success":
        # Show success message
        toast = {
            'is_open': True, 
            'message': 'Project created successfully!', 
            'header': 'Success', 
            'icon': 'success'
        }
        return toast
    else:
        # Handle the error
        toast = {
            'is_open': True, 
            'message': 'There is something wrong!', 
            'header': 'Failure', 
            'icon': 'failure'
        }
        return toast
    
