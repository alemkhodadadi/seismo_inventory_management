from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_inventory, update_table, get_repairs
import pandas as pd
import dash_ag_grid as dag

register_page(__name__, path="/repair")  # Register a page at /page-2


tabs_styles = {
    'height': '44px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}
cell_style = {
    "textAlign": "center", 
    "display": "flex", 
    "justifyContent": "center", 
    "alignItems": "center",
    "borderRight": "1px solid lightgray",
}  # Horizontally and vertically center the content

def layout():
    repairs = get_repairs()
    return html.Div([
        html.Div(
            [
                html.Hr(),
                html.Div([
                    dcc.Link(
                        dbc.Button(
                            "Add Repair", 
                            color="primary",  # Bootstrap button style
                            className="me-1"
                        ),
                        href="/add-repair"  # Set the path for the navigation
                    ),
                    dbc.Button(
                        "Update Table",
                        id="update-table-button-repairs",
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
                id="table-repairs-editable",
                rowData=repairs.to_dict("records"),
                columnDefs=[
                    {"field": i, "cellStyle": cell_style, "headerStyle": cell_style} for i in repairs.columns if i not in ['Number_sum']
                ],
                defaultColDef={"filter": True, 'editable': True},
                dashGridOptions={"pagination": True},
                style={"minHeight":"800px"},
            ),
            dcc.Store(id='table-repairs-editable-changes', data=[]),
        ])
    ],style={"flex": "1"})
    

@callback(
    [
        Output('table-repairs-editable-changes', 'data', allow_duplicate=True),
        Output('update-table-button-repairs', 'disabled', allow_duplicate=True),
    ],
    Input('table-repairs-editable', 'cellValueChanged'),
    State('table-repairs-editable-changes', 'data'),
    prevent_initial_call=True
)
def track_table_changes(event, changes):
    # If no change was detected, return the current data and keep the button disabled

    if event is None or len(event) == 0:
        return changes, True
    if len(event) == 1:
       event = event[0]
    # Extract the updated row from the event
    updated_row = event['data']  # The row that was updated
    row_id = int(event['rowId'])  # Assuming 'id' is a unique identifier
    change = {"rowIndex": row_id, "status": "update", "row":updated_row}
    changes.append(change)
    # We want to enable the button after a change is made
    button_disabled = False  # Enable the button once a change has been detected    
    # Return the updated data and set button state to enabled (button_disabled=False)
    return changes, button_disabled


@callback(
    [
        Output('toast-store', 'data', allow_duplicate=True),
        Output('update-table-button-repairs', 'disabled', allow_duplicate=True)
    ],
    Input('update-table-button-repairs', 'n_clicks'),
    State('table-repairs-editable-changes', 'data'),
    prevent_initial_call=True
)
def update_repairs_table(n_clicks, changes):
    toast = {
        'is_open': False, 
        'message': '', 
        'header': 'Success', 
        'icon': 'success'
    }
    if n_clicks > 0:
        response = update_table(changes, "Inventory_Repair") # the function update_table is quite flexible if the sheetname is defined well
        if response["status"] == "success":
            # Show success message
            toast = {
                'is_open': True, 
                'message': 'Table updated successfully!', 
                'header': 'Success', 
                'icon': 'success'
            }
            
        else:
            print("error updating table:", response["status"])
            # Handle the error
            toast = {
                'is_open': True, 
                'message': 'There is something wrong!', 
                'header': 'Failure :(', 
                'icon': 'failure'
            }
        return toast, True
        
    return toast, True
    