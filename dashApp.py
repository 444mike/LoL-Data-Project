import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import database_manager as dbm
from plot_generator import plot_role_data  # Import the updated plot generation function
import os

# Initialize the Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

# Fetch data with an optional role, minimum games filter, and search term
def fetch_data(role=None, min_games=0, search_query=""):
    # Handle the case when min_games is None
    if min_games is None:
        min_games = 0
    
    query = f"""
        SELECT championName, 
               individualPosition, 
               COUNT(*) as total_games,
               100.0 * SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate
        FROM participants
    """
    conditions = []
    if role:
        conditions.append(f"individualPosition = '{role}'")
    if search_query:
        conditions.append(f"championName LIKE '%{search_query}%'")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " GROUP BY championName, individualPosition"
    if min_games > 0:
        query += f" HAVING COUNT(*) >= {min_games}"
    query += " ORDER BY win_rate DESC;"
    
    # Get data from the database
    data = dbm.get_data(query)
    return data

# Get initial data
data = fetch_data()

# Function to generate HTML table
def generate_table(data):
    return html.Table(
        # Header row
        [html.Tr([
            html.Th("Champion"), 
            html.Th("Image"), 
            html.Th("Role"), 
            html.Th("Total Games"), 
            html.Th("Win Rate (%)")
        ])] +
        # Data rows
        [
            html.Tr([
                html.Td(row['championName']),
                html.Td(html.Img(src=f"assets/champion_images/{row['championName']}.png", style={"width": "50px", "height": "50px"})),
                html.Td(row['individualPosition']),
                html.Td(row['total_games']),
                html.Td(f"{row['win_rate']:.2f}")
            ]) for _, row in data.iterrows()
        ],
        style={
            "width": "100%", 
            "borderCollapse": "collapse", 
            "color": "#dddddd", 
            "margin": "20px auto"
        }
    )

# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("League of Legends - Win Rates by Champion and Role", className="text-center"), width=12)
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.H3("Generate Plots by Role"),
            dbc.ButtonGroup([
                dbc.Button("Generate Top Plot", id='plot-btn-top', n_clicks=0, color="primary"),
                dbc.Button("Generate Jungle Plot", id='plot-btn-jungle', n_clicks=0, color="success"),
                dbc.Button("Generate Middle Plot", id='plot-btn-middle', n_clicks=0, color="info"),
                dbc.Button("Generate Bottom Plot", id='plot-btn-bottom', n_clicks=0, color="warning"),
                dbc.Button("Generate Support Plot", id='plot-btn-support', n_clicks=0, color="danger"),
            ], className="d-flex justify-content-center mb-3"),
            html.Div(id='plot-display', children=[], className="text-center")
        ], width=12)
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.P("Displaying the win rates of each champion by their role (lane):"),
            dbc.ButtonGroup([
                dbc.Button("Top", id='btn-top', n_clicks=0, color="primary"),
                dbc.Button("Jungle", id='btn-jungle', n_clicks=0, color="success"),
                dbc.Button("Middle", id='btn-middle', n_clicks=0, color="info"),
                dbc.Button("Bottom", id='btn-bottom', n_clicks=0, color="warning"),
                dbc.Button("Support", id='btn-support', n_clicks=0, color="danger"),
            ], className="d-flex justify-content-center mb-3"),
            html.Div([
                html.Label("Minimum Number of Games:"),
                dcc.Input(
                    id='min-games-input',
                    type='number',
                    value=0,
                    min=0,
                    step=1,
                    style={'margin-left': '10px', 'width': '100px'}
                )
            ], className="d-flex justify-content-center align-items-center mb-3"),
            html.Div([
                html.Label("Search Champion:"),
                dcc.Input(
                    id='search-input',
                    type='text',
                    placeholder='Enter champion name...',
                    debounce=True,
                    style={'margin-left': '10px', 'width': '200px'}
                )
            ], className="d-flex justify-content-center align-items-center mb-4"),
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(id='win-rate-table', children=generate_table(data)),
            width=12
        )
    ]),
], fluid=True, style={'backgroundColor': '#333333', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'})

# Define callback to update table and plot based on user interactions
@app.callback(
    [Output('win-rate-table', 'children'),
     Output('plot-display', 'children')],
    [
        Input('btn-top', 'n_clicks'),
        Input('btn-jungle', 'n_clicks'),
        Input('btn-middle', 'n_clicks'),
        Input('btn-bottom', 'n_clicks'),
        Input('btn-support', 'n_clicks'),
        Input('plot-btn-top', 'n_clicks'),
        Input('plot-btn-jungle', 'n_clicks'),
        Input('plot-btn-middle', 'n_clicks'),
        Input('plot-btn-bottom', 'n_clicks'),
        Input('plot-btn-support', 'n_clicks'),
        Input('min-games-input', 'value'),
        Input('search-input', 'value')
    ]
)
def update_table_and_plot(n_top, n_jungle, n_middle, n_bottom, n_support,
                          n_plot_top, n_plot_jungle, n_plot_middle, n_plot_bottom, n_plot_support,
                          min_games, search_query):
    ctx = dash.callback_context
    if not ctx.triggered:
        return generate_table(fetch_data(min_games=min_games, search_query=search_query or "")), []

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    role = None

    # Map buttons to roles
    if button_id in ['btn-top', 'plot-btn-top']:
        role = 'TOP'
    elif button_id in ['btn-jungle', 'plot-btn-jungle']:
        role = 'JUNGLE'
    elif button_id in ['btn-middle', 'plot-btn-middle']:
        role = 'MIDDLE'
    elif button_id in ['btn-bottom', 'plot-btn-bottom']:
        role = 'BOTTOM'
    elif button_id in ['btn-support', 'plot-btn-support']:
        role = 'SUPPORT'

    filtered_data = fetch_data(role=role if 'btn' in button_id else None, min_games=min_games, search_query=search_query or "")

    plot_output = []
    if 'plot' in button_id and role:
        plot_path = plot_role_data(role, min_games=min_games)  # Ensure min_games is passed
        plot_output = html.Img(src=f"/assets/{os.path.basename(plot_path)}",
                               style={"width": "70%", "height": "auto", "margin": "0 auto", "display": "block"})

    return generate_table(filtered_data), plot_output


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
