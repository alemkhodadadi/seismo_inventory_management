import plotly.graph_objs as go
import pandas as pd

# Create some date-based data
dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
values = [10, 15, 12, 13, 16, 18, 14, 17, 19, 20]

fig = go.Figure()

# Add the line plot
fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='Value'))

# Update the layout to include a rangeslider for the date axis
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True,  # Show rangeslider
        ),
        type="date"  # Ensure x-axis is treated as dates
    ),
    title="Date-based RangeSlider Example"
)

fig.show()