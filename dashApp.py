import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SOLAR])

# Define the navigation bar
nav_bar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/", style={"color": "white", "fontWeight": "bold", "fontSize": "16px"})),
        dbc.NavItem(dbc.NavLink("Game Duration", href="/gameduration", style={"color": "white", "fontWeight": "bold", "fontSize": "16px"})),
        dbc.NavItem(dbc.NavLink("Champion Performance", href="/statistics", style={"color": "white", "fontWeight": "bold", "fontSize": "16px"})),
    ],
    brand="League of Legends Dashboard",
    brand_href="/",
    color="#084c61",  # A bold contrasting color
    dark=True,
    className="mb-4",
    style={
        "padding": "15px",
        "fontFamily": "Arial, sans-serif",
        "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.3)",  # Stronger shadow for depth
        "borderBottom": "4px solid #00aaff"  # Bright border to create separation
    }
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
