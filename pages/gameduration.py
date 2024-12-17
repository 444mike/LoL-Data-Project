import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Register the page with Dash
dash.register_page(__name__, path="/gameduration", name="Game Duration")

# Layout for the Game Duration page
layout = dbc.Container([
    html.H1("Game Duration Analysis", className="text-center mb-4"),
    html.P("Placeholder: Analyze game durations here.", className="text-center"),
    html.Div([
        html.Label("This page will display stats related to game durations."),
        html.Br(),
        html.P("Add tables, graphs, or charts here as needed!")
    ], style={"textAlign": "center", "marginTop": "20px"})
], fluid=True)
