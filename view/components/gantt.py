import plotly.express as px
import datetime
import pandas as pd

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
