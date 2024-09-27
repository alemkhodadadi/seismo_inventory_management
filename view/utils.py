
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
import datetime
import pandas as pd
# pd.set_option('display.max_rows', None)
def create_gantt(
        data, 
        parameter_name, 
        start_column_name, 
        end_column_name, 
        color, 
        labels, 
        vlinestart:datetime=None,
        vlineend:datetime=None
    ):

    fig = px.timeline(
        data, 
        template="seaborn",
        x_start=start_column_name, 
        x_end=end_column_name, 
        y=parameter_name,
        title='Title',
        color=color,
        labels=labels,
        height=800,
    )

    # if the parameter "zoom_to_date" is not none, it means we need a shorter period to plot. 
    # so we should have the starting time(zoom_to_date_from) and the length(zoom_to_date_length)
    if vlinestart is not None:
        fig.add_vline(x=vlinestart.date, line_width=3, line_color="red")
    if vlineend is not None:
        fig.add_vline(x=vlineend.date, line_width=3, line_color="red")

    fig.update_traces(marker_line_color='rgb(0,0,0)', marker_line_width=2.5, opacity=1)
    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        xaxis_title='Timeline', 
        xaxis=dict(dtick='M1'), font=dict(size=16),
        showlegend=False,
        autosize=True,
        minreducedwidth=800,
    )
    # fig.show()
    return fig

def create_heatmap(availability_df):
    # Create a pivot table to structure the data for the heatmap
    print("kose nanat 3:", availability_df)
    availability_df['Availability'] = (availability_df['Available'] / availability_df['Total']) * 100
    pivot_table = availability_df.pivot_table(index='Instrument', columns='Time Slot', values='Availability')
    print('fucking availability is:', pivot_table)
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,  # Availability values
        x=pivot_table.columns,  # Time slots (x-axis)
        y=pivot_table.index,  # Instruments (y-axis)
        text=pivot_table.values,  # Show availability values as text on the heatmap
        texttemplate="%{text:.1f}%",
        textfont={"size": 12},
        colorscale="Viridis",  # Color scale for availability (can be changed),
        zmin=0,  # Minimum color value (0% availability)
        zmax=100  # Maximum color value (100% availability)
    ))

    fig.update_layout(
        title='Instrument Availability Heatmap',
        xaxis_nticks=36,
        autosize=True,
        height=1000,
        minreducedwidth=800,
    )

    return fig


# Define the global toast as a function so it can be reused
def global_toast():
    return dbc.Toast(
        id='global-toast',
        header='Notification',
        is_open=False,  # Initially hidden
        dismissable=True,  # User can close it
        duration=4000,  # Auto-hide after 4 seconds
        icon="info",  # Default icon, can be changed dynamically
        style={
            "position": "fixed",
            "top": "50%",  # Center the toast vertically
            "left": "50%",  # Center the toast horizontally
            "transform": "translate(-50%, -50%)",  # Ensure it stays centered
            "width": "350px",
            "zIndex": 9999  # Ensure it's on top
        },
    )


def timeslots_for_projects(projects):
    # Convert pickup_date and return_date to datetime if they aren't already
    projects['pickup_date'] = pd.to_datetime(projects['pickup_date'])
    projects['return_date'] = pd.to_datetime(projects['return_date'])
    
    # Extract and combine the pickup and return dates, then drop NaN values
    dates = pd.concat([projects['pickup_date'], projects['return_date']]).dropna()
    
    # Remove duplicates and sort the dates
    unique_dates = sorted(dates.drop_duplicates())
    
    # Create time slots by pairing consecutive dates
    time_slots = [(unique_dates[i], unique_dates[i + 1]) for i in range(len(unique_dates) - 1)]
    
    return time_slots

def generate_instrument_availability(inventory, projects, time_slots):
    # Create an empty list to hold the final rows
    availability_data = []

    # Iterate over all instruments in the inventory table
    for instrument_id in inventory['ID']:
        if instrument_id:
            # Get the total number of instruments for each instrument_id from the inventory
            total_instruments = int(inventory[inventory['ID'] == instrument_id]['Number_sum'].values[0])
            print("print1:", total_instruments)
            # Iterate over each time slot
            for start, end in time_slots:
                # Filter projects that are active during the current time slot
                active_projects = projects[
                    (projects['pickup_date'] <= end) & 
                    (projects['return_date'] >= start)
                ]
                # Calculate how many instruments are occupied during this time slot
                if instrument_id in active_projects.columns:
                    occupied_instruments = pd.to_numeric(active_projects[instrument_id], errors='coerce').fillna(0).astype(int).sum()
                else:
                    occupied_instruments = 0

                # Calculate how many instruments are available
                available_instruments = total_instruments - occupied_instruments

                # Create a dictionary for each row in the final table
                availability_data.append({
                    'Instrument': instrument_id,
                    'Time Slot': f'{start.date()} - {end.date()}',
                    'Total': total_instruments,
                    'Occupied': occupied_instruments,
                    'Available': available_instruments
                })
    
    # Convert the list of dictionaries into a DataFrame
    availability_df = pd.DataFrame(availability_data)
    
    return availability_df