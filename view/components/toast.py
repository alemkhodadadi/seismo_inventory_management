import dash_bootstrap_components as dbc
from dash import dcc

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