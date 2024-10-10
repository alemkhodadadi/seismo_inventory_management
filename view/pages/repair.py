from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_inventory, update_table, get_repairs
import pandas as pd
import dash_ag_grid as dag
from view.styles import cell_style, tab_style, tabs_styles, tab_selected_style

register_page(__name__, path="/repair")  # Register a page at /page-2



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
                    dbc.Button(
                        "Delete selected rows",
                        id="delete-table-button-repairs",
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
                id="table-repairs-editable-container",
                children=[   
                    dag.AgGrid(
                        id="table-repairs-editable",
                        rowData=repairs.to_dict("records"),
                        columnDefs=[
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
                                for i, column in enumerate(repairs.columns) if column not in ['Number_sum', "vid"]
                        ],
                        defaultColDef={"filter": True, 'editable': True},
                        dashGridOptions={"pagination": True},
                        style={"minHeight":"800px"},
                    ),
                ]
            ),
            dcc.Store(id='table-repairs-editable-changes', data=[]),
        ])
    ],style={"flex": "1"})
    

@callback(
    Output("delete-table-button-repairs", "disabled"),
    Input("table-repairs-editable", "selectedRows"),
)
def selected(selectedrows):
    if selectedrows is not None and len(selectedrows) > 0:
        return False
    return True

@callback(
    [
        Output('toast-store', 'data', allow_duplicate=True),
        Output('table-repairs-editable-container', 'children', allow_duplicate=True),
        Output("delete-table-button-repairs", "disabled", allow_duplicate=True),
    ],
    Input("delete-table-button-repairs", "n_clicks"),
    State("table-repairs-editable", "selectedRows"),
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
        repairs = get_repairs()
        changes = []
        print('repaired selected rows are:', selected_rows)
        for row in selected_rows:
            row_id = repairs[
                (repairs['vid'] == row['vid'])
            ].index
            if not row_id.empty:  # Check if we found a matching row
                change = {"rowIndex": row_id[0], "status": "delete", "row": row}  # Use the first matching index
                changes.append(change)  # Append to the list of changes
        response = update_table(changes, "Inventory_Repair")
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
        
    repairs_table_after_update = get_repairs()
    table = dag.AgGrid(
        id="table-repairs-editable",
        rowData=repairs_table_after_update.to_dict("records"),
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
            for i, column in enumerate(repairs_table_after_update.columns) if column not in ['Number_sum', "vid"]
        ],
        defaultColDef={"filter": True, 'editable': True},
        dashGridOptions={"pagination": True, "rowSelection":"multiple"},
        style={"minHeight":"800px"},
    ),
    return toast, table, disabled


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
    