from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_inventory, update_table
import pandas as pd
import dash_ag_grid as dag

register_page(__name__, path="/inventory")  # Register a page at /page-2


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
    inventory = get_inventory()
    return html.Div([
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
                        id="update-table-button-inventory",
                        color="dark",  # Bootstrap button style
                        className="me-1",
                        disabled=True,
                        n_clicks=0
                    ),
                    dbc.Button(
                        "Delete selected rows",
                        id="delete-table-button-inventory",
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
                id="table-inventory-editable-container",
                children=[ 
                    dag.AgGrid(
                        id="table-inventory-editable",
                        rowData=inventory.to_dict("records"),
                        columnDefs=[
                            # its the code to create checkbox at the first column
                            {
                                "field": "Delete", 
                                "checkboxSelection": True, 
                                "headerCheckboxSelection": True, 
                                "width": 50 
                            },
                        ]+[
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
                            for i, column in enumerate(inventory.columns) if column not in ['Number_sum', "vid"]
                        ],
                        defaultColDef={"filter": True, 'editable': True},
                        dashGridOptions={"pagination": True},
                        style={"minHeight":"800px"},
                    ),
                ]
            ),
            dcc.Store(id='table-inventory-editable-changes', data=[]),
        ])
    ],style={"flex": "1"})
    
@callback(
    Output("delete-table-button-inventory", "disabled"),
    Input("table-inventory-editable", "selectedRows"),
)
def selected(selectedrows):
    if selectedrows is not None and len(selectedrows) > 0:
        return False
    return True

@callback(
    [
        Output('toast-store', 'data', allow_duplicate=True),
        Output('table-inventory-editable-container', 'children', allow_duplicate=True),
        Output("delete-table-button-inventory", "disabled", allow_duplicate=True),
    ],
    Input("delete-table-button-inventory", "n_clicks"),
    State("table-inventory-editable", "selectedRows"),
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
        inventory = get_inventory()
        changes = []
        print('inventory selected rows are:', selected_rows)
        for row in selected_rows:
            row_id = inventory[
                (inventory['vid'] == row['vid'])
            ].index
            if not row_id.empty:  # Check if we found a matching row
                change = {"rowIndex": row_id[0], "status": "delete", "row": row}  # Use the first matching index
                changes.append(change)  # Append to the list of changes
        response = update_table(changes, "Inventory")
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
        
    inventory_table_after_update = get_inventory()
    table = dag.AgGrid(
        id="table-inventory-editable",
        rowData=inventory_table_after_update.to_dict("records"),
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
            for i, column in enumerate(inventory_table_after_update.columns) if column not in ['Number_sum', "vid"]
        ],
        defaultColDef={"filter": True, 'editable': True},
        dashGridOptions={"pagination": True, "rowSelection":"multiple"},
        style={"minHeight":"800px"},
    ),
    return toast, table, disabled


@callback(
    [
        Output('table-inventory-editable-changes', 'data'),
        Output('update-table-button-inventory', 'disabled', allow_duplicate=True),
    ],
    Input('table-inventory-editable', 'cellValueChanged'),
    State('table-inventory-editable-changes', 'data'),
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
        Output('update-table-button-inventory', 'disabled')
    ],
    Input('update-table-button-inventory', 'n_clicks'),
    State('table-inventory-editable-changes', 'data'),
    prevent_initial_call=True
)
def update_inventory_table(n_clicks, changes):
    toast = {
        'is_open': False, 
        'message': '', 
        'header': 'Success', 
        'icon': 'success'
    }
    if n_clicks > 0:
        response = update_table(changes, "Inventory") # the function update_table is quite flexible if the sheetname is defined well
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
    