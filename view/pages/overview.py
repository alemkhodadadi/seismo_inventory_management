from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_projects, get_datepicker_dates, update_table, get_projects_table, get_inventory_instruments_number, get_projects_timeline
import pandas as pd
import dash_ag_grid as dag
from view.utils import create_gantt, create_heatmap, timeslots_for_projects, get_slot_index_of_period, create_timeslots, create_data_for_heatmap, generate_instrument_availability, create_pivot_table_for_heatmap
from view.styles import cell_style, tab_style, tabs_styles, tab_selected_style
import numpy as np 

register_page(__name__, path="/")  # Register the home page at the root path
slottype = 'week' # week/month
projects = get_projects()
today = pd.Timestamp.today() 
filtered_period_start = today - pd.DateOffset(months=1)
filtered_period_end = today + pd.DateOffset(months=5)
avai_status = 'Availability'

# here we measure the start and end  for all projects in timeslots in length of week/month
all_projects_start = pd.to_datetime(projects['pickup_date']).min()
all_projects_end = pd.to_datetime(projects['return_date']).max()
timeslots_all_projects = create_timeslots(all_projects_start, all_projects_end, slottype=slottype)

first_value, second_value = get_slot_index_of_period(filtered_period_start, filtered_period_end, timeslots_all_projects)
print('first and second value are:', first_value, second_value)
#creating heatmap for the filtered period. the default filtered period is 6-month starts with one month before today and ends 5 month later than today
data_heatmap_availability = create_data_for_heatmap(filtered_period_start, filtered_period_end, avai_occ=avai_status, slottype=slottype)


slider_items = {i: slot['start_date'] for i, slot in enumerate(timeslots_all_projects)}
step_size = max(1, len(slider_items) // 10)  # there are at least 10 marks
slider_items_range = np.linspace(0, len(slider_items) - 1, num=10, dtype=int)  # Get 10 evenly spaced indices
slider_labels = {int(i): slider_items[i] for i in slider_items_range}
# print("date_items", date_items)

projects_timeline = get_projects_timeline()


def layout():
    return html.Div([
        dcc.Store(id='filtered-dates', data=[filtered_period_start, filtered_period_end]),
        dcc.Store(id='filtered-dates-items', data=[first_value, second_value]),
        dcc.Store(id='slottype', data=slottype),
        dcc.Store(id='avai_status', data=avai_status),
        html.Div(
            [
                html.P("Filters:"),
                html.Div(
                [
                    dcc.RangeSlider(
                        id='date-range-slider',
                        min = 0, 
                        max = len(timeslots_all_projects) -1,
                        step = 1,
                        value=[first_value, second_value],
                        marks=slider_labels,
                        className="px-0"
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown-instruments-availability',
                                    options=[
                                        {'label': 'Availability', 'value': 'Availability'},
                                        {'label': 'Occupation', 'value': 'Occupation'},
                                    ],
                                    value='Availability',  # Default value
                                ),
                                width=3
                            )
                        ],
                        class_name="mt-3"
                    )

                ],style={"width":"100%", "paddingLeft": "150px", "paddingRight": "150px"}),
                
            ]
        ),
        html.Hr(),
        html.Div(
            id="heatmap-container",
            children=[
                dcc.Graph(
                    figure=create_heatmap(data_heatmap_availability, avai_status),
                    style={"width":"100%"}
                ),
            ]
        ),
        html.Div(
            id="gantt-container",
            children=(
                dcc.Graph(
                    figure=create_gantt(
                        data=projects_timeline, 
                        parameter_name="Name",
                        start_column_name="pickup_date",
                        end_column_name="return_date",
                        color="Name",
                        labels={'Sensor_Type': 'Sensor Type'},
                    ),
                ),
            )
        )
    ])

def layout_old():
    projects_pure = get_projects()
    projects_table = get_projects_table()
    projects_timeline = get_projects_timeline()
    inventory_numbers = get_inventory_instruments_number()
    time_slots = timeslots_for_projects(projects_table)
    # heatmap_data = create_pivot_table_for_heatmap(availability_table, 'Availability')
    return html.Div([
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='dropdown-instruments-advailability',
                        options=[
                            {'label': 'Availability', 'value': 'Availability'},
                            {'label': 'Occupation', 'value': 'Occupation'},
                        ],
                        value='Availability',  # Default value
                    ),
                    width=3,
                ),
            ]
        ),
        html.Hr(),
        html.Div(
            id="heatmap-containert",
            children=[
                dcc.Graph(
                    # figure=create_heatmap(heatmap_data, "Availability")
                ),
            ]
        ),
        html.Hr(),
        html.P("Filter based on:"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='dropdown-projects-date',
                                        options=[
                                            {'label': 'None', 'value': 'none'},
                                            {'label': 'Dates', 'value': 'option_dates'},
                                            #{'label': 'Date Range', 'value': 'date_range'}
                                        ],
                                        value='none',  # Default value
                                        placeholder="Select an option",
                                    ),
                                    width=3,
                                ),
                                dbc.Col(
                                    html.Div(id='dropdown-projects-date-content'),
                                    width=9,
                                ),
                            ]
                        )
                    ],
                    width=10
                ),
                dbc.Col(
                    dbc.Button(
                        "Apply", id="apply-date-filter", className="me-2", n_clicks=0, disabled=True
                    ),
                    width=2
                )
            ],
            align="center",
        ),
        html.Hr(),
        dbc.Row(
            id="custom-timeline",
            children=(
                dcc.Graph(
                    figure=create_gantt(
                        data=projects_timeline, 
                        parameter_name="Name",
                        start_column_name="pickup_date",
                        end_column_name="return_date",
                        color="Name",
                        labels={'Sensor_Type': 'Sensor Type'},
                    ),
                ),
            )
        )

    ],style={"flex": "1"})


@callback(
    [
        Output('filtered-dates-items', 'data'),
        Output('filtered-dates', 'data'),
        Output('heatmap-container', 'children')
    ],
    Input('date-range-slider', 'value'),
    State('slottype', 'data'),
    State('avai_status', 'data')
)
def update_output(values, slottype, status):
    # Convert the slider int values back to dates
    start_index_in_slots = values[0]
    end_index_in_slots = values[1]
    new_filtered_period_start = pd.to_datetime(timeslots_all_projects[start_index_in_slots]["start_date"])
    new_filtered_period_end = pd.to_datetime(timeslots_all_projects[end_index_in_slots]["end_date"])


    #creating the data for heatmap based on new dates
    data_heatmap_availability = create_data_for_heatmap(
        new_filtered_period_start, 
        new_filtered_period_end, 
        avai_occ=status, 
        slottype=slottype
    )

    newchart = dcc.Graph(
                    figure=create_heatmap(data_heatmap_availability, avai_status),
                    style={"width":"100%"}
                ),

    return values, [new_filtered_period_start, new_filtered_period_end], newchart

    print('new data is ', data_heatmap_availability)

    # print("start:", start_date)
    # print("end is:", end_date)
    # return f'Selected range: {start_date} to {end_date}'


@callback(Output('overview-tabs-content', 'children'),
              [Input('overview-tabs', 'value')])

def render_content(tab):
    projects_pure = get_projects()
    projects_table = get_projects_table()
    projects_timeline = get_projects_timeline()
    inventory_numbers = get_inventory_instruments_number()
    time_slots = timeslots_for_projects(projects_table)
    # availability_table = generate_instrument_availability(inventory_numbers, projects_pure, time_slots)
    
    if tab == 'inventory-availability':
        # heatmap_data = create_pivot_table_for_heatmap(availability_table, 'Availability')
        return html.Div(
            [
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id='dropdowdn-instruments-availability',
                                options=[
                                    {'label': 'Availability', 'value': 'Availability'},
                                    {'label': 'Occupation', 'value': 'Occupation'},
                                ],
                                value='Availability',  # Default value
                            ),
                            width=3,
                        ),
                    ]
                ),
                html.Hr(),
                html.Div(
                    id="heatmap-containerr",
                    children=[
                        dcc.Graph(
                            # figure=create_heatmap(heatmap_data, "Availability")
                        ),
                    ]
                )
            ]
        )
    elif tab == 'projects-timeline':
        return html.Div(
            [
                html.Hr(),
                html.P("Filter based on:"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='dropdown-projects-date',
                                                options=[
                                                    {'label': 'None', 'value': 'none'},
                                                    {'label': 'Dates', 'value': 'option_dates'},
                                                    #{'label': 'Date Range', 'value': 'date_range'}
                                                ],
                                                value='none',  # Default value
                                                placeholder="Select an option",
                                            ),
                                            width=3,
                                        ),
                                        dbc.Col(
                                            html.Div(id='dropdown-projects-date-content'),
                                            width=9,
                                        ),
                                    ]
                                )
                            ],
                            width=10
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Apply", id="apply-date-filter", className="me-2", n_clicks=0, disabled=True
                            ),
                            width=2
                        )
                    ],
                    align="center",
                ),
                html.Hr(),
                dbc.Row(
                    id="custom-timeline",
                    children=(
                        dcc.Graph(
                            figure=create_gantt(
                                data=projects_timeline, 
                                parameter_name="Name",
                                start_column_name="pickup_date",
                                end_column_name="return_date",
                                color="Name",
                                labels={'Sensor_Type': 'Sensor Type'},
                            ),
                        ),
                    )
                )
            ]
        )
    
@callback(
    Output('apply-date-filter', 'disabled'),
    [
        Input('start-date-picker', 'date'),
        Input('end-date-picker', 'date')
    ]
)
def make_apply_btn_active(start, end):
    return False

@callback(
    [
        Output('custom-timeline', 'children'),  # Second output
        Output('apply-date-filter', 'disabled', allow_duplicate=True)
    ],
    Input('apply-date-filter', 'n_clicks'),
    State('start-date-picker', 'date'),   # Get the value of the start date
    State('end-date-picker', 'date'),      # Get the value of the end date
    prevent_initial_call=True
)

def check_dates(n_clicks, from_date, to_date):
    # Convert string dates to Timestamps
    start_period = pd.Timestamp(from_date)
    end_period = pd.Timestamp(to_date)

    # Assuming `get_projects_timeline()` returns a DataFrame
    projects_timeline = get_projects_timeline()

    # Ensure that pickup_date and return_date are in datetime format
    projects_timeline['pickup_date'] = pd.to_datetime(projects_timeline['pickup_date'])
    projects_timeline['return_date'] = pd.to_datetime(projects_timeline['return_date'])

    # Filter the DataFrame based on the date range
    projects_timeline = projects_timeline[
        (projects_timeline['pickup_date'] <= end_period) & 
        (projects_timeline['return_date'] >= start_period)
    ]

    return dcc.Graph(
        figure=create_gantt(
            data=projects_timeline, 
            parameter_name="Name", 
            start_column_name="pickup_date", 
            end_column_name="return_date",
            color="Name",
            labels={'Sensor_Type': 'Sensor Type'},
        ),
    ), True
    

@callback(
    [
        Output('heatmap-container', 'children', allow_duplicate=True),
        Output('avai_status', 'data'),
    ],
    
    Input('dropdown-instruments-availability', 'value'),
    State('filtered-dates', 'data'),
    prevent_initial_call = True
)
def change_heatmap_mode(selected_option, dates):
    print('selected_option is:', selected_option)
    print('dates is:', dates)
    print('filtered_period_end is:', filtered_period_end)
    data_heatmap_availability = create_data_for_heatmap(pd.to_datetime(dates[0]), pd.to_datetime(dates[1]), avai_occ=selected_option, slottype=slottype)
    return dcc.Graph(
        figure=create_heatmap(data_heatmap_availability, selected_option),
        style={"width":"100%"}
    ), selected_option


    # projects_table = get_projects_table()
    # projects_pure = get_projects()
    # inventory_numbers = get_inventory_instruments_number()
    # time_slots = timeslots_for_projects(projects_table)
    # availability_table = generate_instrument_availability(inventory_numbers, projects_pure, time_slots)
    # heatmap_data = create_pivot_table_for_heatmap(availability_table, selected_option)
    # return dcc.Graph(
    #     figure=create_heatmap(heatmap_data, selected_option)
    # ),
    return ''

    
@callback(
    Output('dropdown-projects-date-content', 'children'),
    [Input('dropdown-projects-date', 'value')]
)

def display_date_picker(selected_option):
    earliest_day, latest_day, today = get_datepicker_dates()
    if selected_option == 'none':
        return html.Div()  # No date picker if "None" is selected
    
    elif selected_option == 'option_dates':
        # Display two DatePickerSingle components for start and end date
        return html.Div(
            [
                html.Div(
                    [
                        html.Label("From: "),
                        dcc.DatePickerSingle(
                            min_date_allowed=earliest_day,
                            id='start-date-picker',
                            placeholder='From',
                            date='2024-07-01'
                        ),
                    ], style={'display': 'inline-block', 'margin-right': '20px'}
                ),
                
                html.Div(
                    [
                        html.Label("To: "),
                        dcc.DatePickerSingle(
                            max_date_allowed=latest_day,
                            id='end-date-picker',
                            placeholder='To',
                            date=latest_day
                        ),
                    ], style={'display': 'inline-block'}
                )
            ]
        )
    
    elif selected_option == 'date_range':
        # Display a DatePickerRange component
        return dcc.DatePickerRange(
            id='date-range-picker',
            start_date_placeholder_text='Start Date',
            end_date_placeholder_text='End Date'
        ) 
