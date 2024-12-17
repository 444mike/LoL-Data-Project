import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR])

# Define the navigation bar
nav_bar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Game Duration", href="/gameduration")),  # New link
    ],
    brand="League of Legends Dashboard",
    brand_href="/",
    color="primary",
    dark=True
)

# Define the layout
app.layout = dbc.Container([
    dcc.Location(id="url"),  # Tracks the current page URL
    nav_bar,                 # Navigation bar
    dash.page_container      # Container to load pages dynamically
], fluid=True)

# Run the server
if __name__ == "__main__":
    app.run_server(debug=False)
