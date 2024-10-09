
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta, datetime
from data.data import get_projects, get_inventory_instruments_number
import pandas as pd
import numpy as np

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
        xaxis=dict(
            dtick='M1',
            tickfont=dict(size=10),  # Set font size for labels
            ticks='outside',  # Show tick marks outside
            ticklen=10,  # Length of tick marks
            tickwidth=2,  # Width of tick marks
            tickcolor='black',  # Color of tick marks
            automargin=True  # Automatically adjust margins to fit labels
        ), 
        font=dict(size=16),
        showlegend=False,
        autosize=True,
        minreducedwidth=800,
        yaxis=dict(
            title='',  # Remove y-axis title
            tickfont=dict(size=10),  # Set font size for labels
            ticks='outside',  # Show tick marks outside
            ticklen=10,  # Length of tick marks
            tickwidth=2,  # Width of tick marks
            tickcolor='black',  # Color of tick marks
            automargin=True  # Automatically adjust margins to fit labels
        ),
        margin=dict(
            l=150,  # Left margin (space for y-axis labels)
            r=150,   # Right margin
        ),
    )
    # fig.show()
    return fig

def create_heatmap(pivot_table, title):
    availability_text = np.where(
        pivot_table.values == -1,  # Check if Availability is -1 (Total is 0)
        "-",  # Display "-" if Total is 0 (represented by -1)
        np.round(pivot_table.values, 0).astype(int).astype(str)  # Round to nearest integer and convert to string
    )
    #colorscale is a 2-d array. if z component is divided by 4 values (0-25, 25-50, 50-75, 75-100)
    # there should be 4 arrayes in the colorscale showing each portion in z . 
    colorscale = [
        [0, "rgb(255, 255, 178)"],
        [0.25, "rgb(255, 255, 178)"],

        [0.25, "rgb(254, 204, 92)"],
        [0.50, "rgb(254, 204, 92)"],

        [0.50, "rgb(253, 141, 60)"],
        [0.75, "rgb(253, 141, 60)"],

        [0.75, "rgb(240, 59, 32)"],
        [0.99, "rgb(240, 59, 32)"],

        [1, "rgb(189, 0, 38)"],
    ]

    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,  # Availability values
        x=pivot_table.columns,  # Time slots (x-axis)
        y=pivot_table.index,  # Instruments (y-axis)
        text=availability_text,  # Show availability values as text on the heatmap
        texttemplate="%{text}",
        textfont={"size": 9},
        hoverinfo='text',  # Only show custom hover text
        hovertemplate='Instrument: %{y}<br>Time Slot: %{x}<br>Availability: %{text}<extra></extra>',  # Customize hover text
        colorscale=colorscale,  # Color scale for availability (can be changed),
        zmin=0,  # Minimum color value (0% availability)
        zmax=100  # Maximum color value (100% availability)
    ))

    fig.update_layout(
        title=title,
        xaxis_nticks=36,
        autosize=True,
        height=1000,
        minreducedwidth=800,
        margin=dict(
            l=150,  # Left margin (space for y-axis labels)
            r=150,   # Right margin
        ),
        yaxis=dict(
            title='',  # Remove y-axis title
            tickfont=dict(size=10),  # Set font size for labels
            ticks='outside',  # Show tick marks outside
            ticklen=10,  # Length of tick marks
            tickwidth=2,  # Width of tick marks
            tickcolor='black',  # Color of tick marks
            automargin=True  # Automatically adjust margins to fit labels
        ),
        xaxis=dict(
            title='',  # Remove y-axis title
            tickfont=dict(size=10),  # Set font size for labels
            ticks='outside',  # Show tick marks outside
            ticklen=10,  # Length of tick marks
            tickwidth=2,  # Width of tick marks
            tickcolor='black',  # Color of tick marks
            automargin=True  # Automatically adjust margins to fit labels
        ),

    )

    return fig

def create_pivot_table_for_heatmap(data, avai_occ):
    # Create a pivot table to structure the data for the heatmap
    if avai_occ == 'Occupation':
        data['Occupation'] = np.where(
            data['Total'] == 0, 
            -1,  # NaN will be replaced by "-" in the display
            (1 - (data['Available'] / data['Total'])) * 100  # Calculate occupation as the opposite of availability
        )
        pivot_table = data.pivot_table(index='Instrument', columns='Time Slot', values='Occupation')
    else:  # Default case for 'availability'
        data['Availability'] = np.where(
            data['Total'] == 0, 
            -1,  # NaN will be replaced by "-" in the display
            (data['Available'] / data['Total']) * 100
        )
        pivot_table = data.pivot_table(index='Instrument', columns='Time Slot', values='Availability')
    
    return pivot_table


def create_data_for_heatmap(start, end, avai_occ, slottype="week"):
    print('create_data_for_heatmap called:', start, end, avai_occ, slottype)
    inventory_numbers = get_inventory_instruments_number()
    print(1)
    print(start, end, slottype)
    time_slots = create_timeslots(start, end, slottype=slottype)
    print(2)
    availability_table = generate_instrument_availability(inventory_numbers, time_slots)
    print(3)
    heatmap_data = create_pivot_table_for_heatmap(availability_table, avai_occ)
    print('returning heatmap_data')
    return heatmap_data

def get_slot_index_of_period(periodstart, periodend, allslots):
    #we have to set the time part of periodstart and periodend 
    #to have a clean date comparison with the dates in the slots
    periodstart = periodstart.replace(hour=0, minute=0, second=0, microsecond=0)
    periodend = periodend.replace(hour=0, minute=0, second=0, microsecond=0)
    slot_index_that_periodstart_is_in = next((i for i, slot in enumerate(allslots) if pd.to_datetime(slot['start_date']) <= periodstart <= pd.to_datetime(slot['end_date'])), None)
    slot_index_that_periodend_is_in = next((i for i, slot in enumerate(allslots) if pd.to_datetime(slot['start_date']) <= periodend <= pd.to_datetime(slot['end_date'])), None)
    return slot_index_that_periodstart_is_in, slot_index_that_periodend_is_in

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
            "zIndex": 9  # Ensure it's on top
        },
    )


def timeslots_for_projects(projects):
    # Extract and combine the pickup and return dates, then drop NaN values
    dates = pd.concat([pd.to_datetime(projects['pickup_date']), pd.to_datetime(projects['return_date'])]).dropna()
    # Remove duplicates and sort the dates
    unique_dates = sorted(dates.drop_duplicates())
    
    # Create time slots by pairing consecutive dates
    time_slots = [(unique_dates[i], unique_dates[i + 1]) for i in range(len(unique_dates) - 1)]
    
    return time_slots

def generate_instrument_availability(inventory, time_slots):
    # Create an empty list to hold the final rows
    availability_data = []
    projects = get_projects()
    # Iterate over all instruments in the inventory table
    for instrument_id in inventory['ID']:
        if instrument_id:
            # Get the total number of instruments for each instrument_id from the inventory
            total_instruments = int(inventory[inventory['ID'] == instrument_id]['Number_sum'].values[0])
            # Iterate over each time slot
            for i, timeslot in enumerate(time_slots):
                start = timeslot["start_date"]
                end = timeslot["end_date"]
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
                    'Time Slot': f'{start} - {end}',
                    'Total': total_instruments,
                    'Occupied': occupied_instruments,
                    'Available': available_instruments
                })
    
    # Convert the list of dictionaries into a DataFrame
    availability_df = pd.DataFrame(availability_data)
    
    return availability_df


def create_timeslots(start_date, end_date, slottype='week'):
    # List to hold the result
    slots = []
    if slottype == 'week':
        # Get the first Monday on or after the start date
        print('type is:', type(start_date))
        start_date = start_date - timedelta(days=start_date.weekday())
        
        while start_date <= end_date:
            week_number = start_date.isocalendar()[1]  # Get week number
            year = start_date.isocalendar()[0]  # Get the year
            period_end_date = start_date + timedelta(days=6)  # End of the week
            slots.append({
                'week': week_number,
                'year': year,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': min(period_end_date, end_date).strftime('%Y-%m-%d')
            })
            start_date += timedelta(weeks=1)  # Move to the next week

    elif slottype == 'month':
        # Align the start date to the first day of the current month
        start_date = start_date.replace(day=1)
        
        while start_date <= end_date:
            month_number = start_date.month  # Get month number
            year = start_date.year  # Get the year
            # Get the last day of the month
            next_month = start_date.replace(day=28) + timedelta(days=4)  # Always get next month
            period_end_date = (next_month - timedelta(days=next_month.day)).date()  # Last day of the current month
            
            # Convert period_end_date to datetime for comparison
            period_end_date = datetime.combine(period_end_date, datetime.min.time())
            
            slots.append({
                'month': month_number,
                'year': year,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': min(period_end_date, end_date).strftime('%Y-%m-%d')
            })
            # Move to the next month
            start_date = (start_date + timedelta(days=32)).replace(day=1)

    return slots