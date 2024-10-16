from dash import html, register_page, dcc, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_projects, get_datepicker_dates, get_projects_timeline
import pandas as pd
from view.utils import create_gantt, create_heatmap, get_rangeslider_data
from view.styles import cell_style, tab_style, tabs_styles, tab_selected_style
import numpy as np 

register_page(__name__, path="/")  # Register the home page at the root path


###############defining initial conditions for the data
projects = get_projects()
today = pd.Timestamp.today() 
#we define a period with two optional dates for the data te be filtered at the beginning. 
#it starts from the previous month and ends in 5 the next 5th month
filtered_period_start = today - pd.DateOffset(months=1)
filtered_period_end = today + pd.DateOffset(months=5)
#1-slottype, 2-instrument-type, 3-instrument-availability and 4-filtered-dates
period_slottype = 'month' # week/month
instrument_availability = 'Availability'
instrument_type = 'All'

timeslots_all_projects, rangeslider_val_1, rangeslider_val_2, slider_labels = get_rangeslider_data(
    period_slottype,
    filtered_period_start,
    filtered_period_end
)

#creating heatmap for the filtered period. the default filtered period is 6-month starts with one month before today and ends 5 month later than today
initial_heatmap = create_heatmap(
    filtered_period_start, 
    filtered_period_end, 
    type=instrument_type,
    availability=instrument_availability, 
    slottype=period_slottype
)


################generating data for the ganttchart
#here we just need to filter the projects table based on the 
#starttime and endtime of the optional filtering period
projects_timeline = get_projects_timeline()
projects_timeline = projects_timeline[pd.to_datetime(projects_timeline['return_date']) <= filtered_period_end]


def layout():
    return html.Div([
        dcc.Store(id='filtered-dates', data=[filtered_period_start, filtered_period_end]),
        dcc.Store(id='filtered-dates-items', data=[rangeslider_val_1, rangeslider_val_2]),
        dcc.Store(id='period_slottype', data=period_slottype),
        dcc.Store(id='instrument_availability', data=instrument_availability),
        dcc.Store(id='instrument_type', data=instrument_type),
        dcc.Store(id='timeslots_all_projects', data=timeslots_all_projects),
        html.Div(
            [
                html.Div(
                [
                    html.Div(
                        [
                            html.Span('Filtered period: ') ,
                            html.Span(id="filtered-date-start-span", children=filtered_period_start.date().strftime('%d %B %Y'), className="mx-2 text-secondary font-weight-bold") ,
                            html.Span('-'),
                            html.Span(id="filtered-date-end-span", children=filtered_period_end.date().strftime('%d %B %Y'), className="mx-2 text-secondary font-weight-bold") ,
                        ],
                        style={"flexDirection": "row"},
                        className="my-4"
                    ),
                    html.Div(
                        id="date-range-slider-container", 
                        children=[
                            dcc.RangeSlider(
                                id='date-range-slider',
                                min = 0, 
                                max = len(timeslots_all_projects) -1,
                                step = 1,
                                value=[rangeslider_val_1, rangeslider_val_2],
                                marks=slider_labels,
                                className="px-0"
                            ),
                        ]
                    ),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown-period-slottype',
                                    options=[
                                        {'label': 'Weekly', 'value': 'week'},
                                        {'label': 'Monthly', 'value': 'month'},
                                    ],
                                    value=period_slottype,  # Default value
                                ),
                                width=3
                            ),
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
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='dropdown-instruments-type',
                                    options=[
                                        {'label': 'All', 'value': 'All'},
                                        {'label': 'Instruments', 'value': 'Instrument'},
                                        {'label': 'Accessories', 'value': 'Accessory'}
                                    ],
                                    value='All',  # Default value
                                ),
                                width=3
                            )
                        ],
                        class_name="mt-3"
                    )

                ],style={"width":"100%", "paddingLeft": "150px", "paddingRight": "150px"}),
            ],
        ),
        html.Hr(),
        html.Div(
            id="heatmap-container",
            children=[
                dcc.Graph(
                    figure=initial_heatmap,
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


@callback(
    [
        Output('filtered-dates-items', 'data'),
        Output('filtered-dates', 'data'),
        Output('filtered-date-start-span', 'children'),
        Output('filtered-date-end-span', 'children'),
        Output('heatmap-container', 'children'),
        Output('gantt-container', 'children')
    ],
    Input('date-range-slider', 'value'),
    State('timeslots_all_projects', 'data'),
    State('period_slottype', 'data'),
    State('instrument_availability', 'data'),
    State('instrument_type', 'data')
)
def update_output(values, timeslots_all_projects, period_slottype, availability, type):
    # Convert the slider int values back to dates
    start_index_in_slots = values[0]
    end_index_in_slots = values[1]

    new_filtered_period_start = pd.to_datetime(timeslots_all_projects[start_index_in_slots]["start_date"])
    new_filtered_period_end = pd.to_datetime(timeslots_all_projects[end_index_in_slots]["end_date"])

    #creating the data for heatmap based on new dates
    new_heatmap_fig = create_heatmap(
        new_filtered_period_start, 
        new_filtered_period_end, 
        availability=availability, 
        type=type,
        slottype=period_slottype
    )

    projects_timeline = get_projects_timeline()
    newprojects_timeline = projects_timeline[pd.to_datetime(projects_timeline['return_date']) <= new_filtered_period_end]

    new_heatmap = dcc.Graph(
                    figure=new_heatmap_fig,
                    style={"width":"100%"}
                ),
    
    new_ganttchart = dcc.Graph(
                    figure=create_gantt(
                        data=newprojects_timeline, 
                        parameter_name="Name",
                        start_column_name="pickup_date",
                        end_column_name="return_date",
                        color="Name",
                        labels={'Sensor_Type': 'Sensor Type'},
                    ),
                ),
    


    return values, [new_filtered_period_start, new_filtered_period_end], new_filtered_period_start.date().strftime('%d %B %Y'), new_filtered_period_end.date().strftime('%d %B %Y'), new_heatmap, new_ganttchart

    
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
        Output('date-range-slider-container', 'children', allow_duplicate=True),
        Output('heatmap-container', 'children', allow_duplicate=True),
        Output('filtered-date-start-span', 'children', allow_duplicate=True),
        Output('filtered-date-end-span', 'children', allow_duplicate=True),
        Output('period_slottype', 'data'),
        Output('timeslots_all_projects', 'data', allow_duplicate=True),
    ],
    
    Input('dropdown-period-slottype', 'value'), # if we have any change in slottype dropdown, this functions will be called
    State('dropdown-instruments-type', 'value'), # it takes the value of 1-slottype, 2-instrument-type, 3-instrument-availability and 4-filtered-dates
    State('dropdown-instruments-availability', 'value'),
    State('filtered-dates', 'data'),
    prevent_initial_call = True
)
def change_period_slottype(selected_option, type, availability, dates):
    new_heatmap_fig = create_heatmap(
        pd.to_datetime(dates[0]), 
        pd.to_datetime(dates[1]), 
        availability=availability, 
        type=type, slottype=selected_option
    )
    
    new_timeslots_all_projects, new_rangeslider_val_1, rangeslider_val_2, new_slider_labels = get_rangeslider_data(
        selected_option, 
        pd.to_datetime(dates[0]), 
        pd.to_datetime(dates[1])
    )


    new_rangeslider = dcc.RangeSlider(
        id='date-range-slider',
        min = 0,
        max = len(new_timeslots_all_projects) -1,
        step = 1,
        value=[new_rangeslider_val_1, rangeslider_val_2],
        marks=new_slider_labels,
        className="px-0"
    ),

    new_heatmap = dcc.Graph(
        figure=new_heatmap_fig,
        style={"width":"100%"}
    )

    new_text_filtering_start = html.Span(id="filtered-date-start-span", children=pd.to_datetime(dates[0]).date().strftime('%d %B %Y'), className="mx-2 text-secondary font-weight-bold") ,
    new_text_filtering_end = html.Span(id="filtered-date-end-span", children=pd.to_datetime(dates[1]).date().strftime('%d %B %Y'), className="mx-2 text-secondary font-weight-bold") ,

    return new_rangeslider, new_heatmap, new_text_filtering_start, new_text_filtering_end, selected_option, new_timeslots_all_projects

@callback(
    [
        Output('heatmap-container', 'children', allow_duplicate=True),
        Output('instrument_availability', 'data'),
    ],
    
    Input('dropdown-instruments-availability', 'value'),
    State('dropdown-instruments-type', 'value'),
    State('dropdown-period-slottype', 'value'),
    State('filtered-dates', 'data'),
    prevent_initial_call = True
)
def change_heatmap_mode(selected_option, type, slottype, dates):

    heatmap = create_heatmap(pd.to_datetime(
        dates[0]), 
        pd.to_datetime(dates[1]), 
        availability=selected_option, 
        type=type, slottype=slottype
    )
    return dcc.Graph(
        figure=heatmap,
        style={"width":"100%"}
    ), selected_option

@callback(
    [
        Output('heatmap-container', 'children', allow_duplicate=True),
        Output('instrument_type', 'data'),
    ],
    
    Input('dropdown-instruments-type', 'value'),
    State('dropdown-instruments-availability', 'value'),
    State('dropdown-period-slottype', 'value'),
    State('filtered-dates', 'data'),
    prevent_initial_call = True
)
def change_heatmap_mode(selected_option, availability, slottype, dates):
    new_heatmap_fig = create_heatmap(
        pd.to_datetime(dates[0]), 
        pd.to_datetime(dates[1]), 
        availability=availability, 
        type=selected_option, slottype=slottype
    )
    return dcc.Graph(
        figure=new_heatmap_fig,
        style={"width":"100%"}
    ), selected_option


    
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
