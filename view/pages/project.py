from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_projects, get_datepicker_dates, update_table, get_projects_table, get_inventory_instruments_number, get_projects_timeline
import pandas as pd
import dash_ag_grid as dag
from view.utils import create_gantt, create_heatmap, timeslots_for_projects, generate_instrument_availability, create_pivot_table_for_heatmap
from view.styles import cell_style

register_page(__name__, path="/project")  # Register the home page at the root path

def layout():
    projects_table = get_projects_table()
    return html.Div([
        html.Div(
            [
                html.Hr(),
                html.Div([
                    dcc.Link(
                        dbc.Button(
                            "Create Project", 
                            color="primary",  # Bootstrap button style
                            className="me-1"
                        ),
                        href="/add-project"  # Set the path for the navigation
                    ),
                    dbc.Button(
                        "Update Table",
                        id="update-table-button-projects",
                        color="dark",  # Bootstrap button style
                        className="me-1",
                        disabled=True,
                        n_clicks=0
                    ),
                    dbc.Button(
                        "Delete selected rows",
                        id="delete-table-button-projects",
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
            html.Div(
                id="table-projects-editable-container",
                children=[
                    dag.AgGrid(
                        id="table-projects-editable",
                        rowData=projects_table.to_dict("records"),
                        columnDefs=
                        
                        [
                            # its the code to create checkbox at the first column
                            {
                                "field": "Delete", 
                                "checkboxSelection": True, 
                                "headerCheckboxSelection": True, 
                                "width": 50 
                            },
                        ]+
                        [
                            {
                                "field": column, 
                                "cellStyle": cell_style, 
                                "headerStyle": cell_style, 
                                "maxWidth":75
                            } 
                            if i>4 else 
                            {
                                "field": column, 
                                "cellStyle": cell_style, 
                                "headerStyle": cell_style
                            } 
                            for i, column in enumerate(projects_table.columns) if column not in ['vid']
                        ],
                        defaultColDef={"filter": True, 'editable': True},
                        dashGridOptions={"pagination": True, "rowSelection":"multiple"},
                        style={"minHeight":"800px"},
                    ),
                ]
            ),
            dcc.Store(id='table-projects-editable-changes', data=[]),
        ])
    
    ],style={"flex": "1"})




@callback(
    Output("delete-table-button-projects", "disabled"),
    Input("table-projects-editable", "selectedRows"),
)
def selected(selectedrows):
    if selectedrows is not None and len(selectedrows) > 0:
        return False
    return True

@callback(
    [
        Output('toast-store', 'data', allow_duplicate=True),
        Output('table-projects-editable-container', 'children', allow_duplicate=True),
        Output("delete-table-button-projects", "disabled", allow_duplicate=True),
    ],
    Input("delete-table-button-projects", "n_clicks"),
    State("table-projects-editable", "selectedRows"),
    prevent_initial_call=True
)
def delete_selected_rows(n_clicks, selected_rows):
    toast = {
        'is_open': False, 
        'message': '', 
        'header': 'Success :)', 
        'icon': 'success'
    }
    disabled = True
    
    if n_clicks > 0 and len(selected_rows)>0:
        projects_data = get_projects_table()
        changes = []
        for row in selected_rows:
            row_id = projects_data[
                (projects_data['Projects'] == row['Projects']) & 
                (projects_data['Leading Institution'] == row['Leading Institution']) 
            ].index
            if not row_id.empty:  # Check if we found a matching row
                change = {"rowIndex": row_id[0], "status": "delete", "row": row}  # Use the first matching index
                changes.append(change)  # Append to the list of changes
        response = update_table(changes, "Projects")
        if response["status"] == "success":
            # Show success message
            toast = {
                'is_open': True, 
                'message': 'Table updated successfully!', 
                'header': 'Success :)', 
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
            disabled = False
        
    projects_table_after_update = get_projects_table()
    table = dag.AgGrid(
        id="table-projects-editable",
        rowData=projects_table_after_update.to_dict("records"),
        columnDefs=
        
        [
            # its the code to create checkbox at the first column
            {
                "field": "Delete", 
                "checkboxSelection": True, 
                "headerCheckboxSelection": True, 
                "width": 50 
            },
        ]+
        [
            {
                "field": column, 
                "cellStyle": cell_style, 
                "headerStyle": cell_style, 
                "maxWidth":150
            } 
            if i>4 else 
            {
                "field": column, 
                "cellStyle": cell_style, 
                "headerStyle": cell_style
            } 
            for i, column in enumerate(projects_table_after_update.columns)
        ],
        defaultColDef={"filter": True, 'editable': True},
        dashGridOptions={"pagination": True, "rowSelection":"multiple"},
        style={"minHeight":"800px"},
    ),
    return toast, table, disabled


@callback(
    [
        Output('table-projects-editable-changes', 'data'),
        Output('update-table-button-projects', 'disabled', allow_duplicate=True),
    ],
    Input('table-projects-editable', 'cellValueChanged'),
    State('table-projects-editable-changes', 'data'),
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
        Output('toast-store', 'data',  allow_duplicate=True),
        Output('update-table-button-projects', 'disabled', allow_duplicate=True)
    ],
    Input('update-table-button-projects', 'n_clicks'),
    State('table-projects-editable-changes', 'data'),
    prevent_initial_call=True
)
def update_projects_table(n_clicks, changes):
    toast = {
        'is_open': False, 
        'message': '', 
        'header': 'Success :)', 
        'icon': 'success'
    }
    disabled = True
    if n_clicks > 0:
        response = update_table(changes, "Projects")
        if response["status"] == "success":
            # Show success message
            toast = {
                'is_open': True, 
                'message': 'Table updated successfully!', 
                'header': 'Success :)', 
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
            disabled = False
        
    return toast, disabled
