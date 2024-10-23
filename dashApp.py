# dash_app.py

import dash
from dash import dcc, html, dash_table
import dash.dependencies as dd
import database_manager as dbm

# Initialize the Dash app
app = dash.Dash(__name__)

# Fetch data with an optional role and minimum games filter
def fetch_data(role=None, min_games=0):
    query = f"""
        SELECT championName, 
               individualPosition, 
               COUNT(*) as total_games,
               100.0 * SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate
        FROM participants
    """
    if role:
        query += f" WHERE individualPosition = '{role}'"
    query += " GROUP BY championName, individualPosition"
    query += f" HAVING total_games >= {min_games}"
    query += " ORDER BY win_rate DESC;"
    return dbm.get_data(query)

# Get initial data with no role filter and minimum 0 games
data = fetch_data()

# Define the layout of the app
app.layout = html.Div([
    html.H1("League of Legends - Win Rates by Champion and Role"),
    html.P("Displaying the win rates of each champion by their role (lane):"),
    html.Div([
        html.Button("Top", id='btn-top', n_clicks=0),
        html.Button("Jungle", id='btn-jungle', n_clicks=0),
        html.Button("Middle", id='btn-middle', n_clicks=0),
        html.Button("Bottom", id='btn-bottom', n_clicks=0),
        html.Button("Support", id='btn-support', n_clicks=0),
    ], style={'margin-bottom': '20px', 'display': 'flex', 'justify-content': 'center', 'gap': '10px'}),
    html.Div([
        html.Label("Minimum Number of Games:"),
        dcc.Input(
            id='min-games-input',
            type='number',
            value=0,
            min=0,
            step=1,
            style={'margin-left': '10px'}
        )
    ], style={'margin-bottom': '20px', 'textAlign': 'center', 'color': '#dddddd'}),
    dash_table.DataTable(
        id='win-rate-table',
        columns=[
            {"name": "Champion", "id": "championName"},
            {"name": "Role", "id": "individualPosition"},
            {"name": "Total Games", "id": "total_games"},
            {"name": "Win Rate (%)", "id": "win_rate"}
        ],
        data=data.to_dict('records'),
        page_size=15,
        sort_action="native",
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#444444', 'color': 'white', 'fontWeight': 'bold'},
        style_data={'backgroundColor': '#222222', 'color': 'white'},
    )
], style={
    'backgroundColor': '#333333', 
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})

# Define callback to update data based on the button clicked and input value
@app.callback(
    dd.Output('win-rate-table', 'data'),
    [
        dd.Input('btn-top', 'n_clicks'),
        dd.Input('btn-jungle', 'n_clicks'),
        dd.Input('btn-middle', 'n_clicks'),
        dd.Input('btn-bottom', 'n_clicks'),
        dd.Input('btn-support', 'n_clicks'),
        dd.Input('min-games-input', 'value')
    ]
)
def update_table(n_top, n_jungle, n_middle, n_bottom, n_support, min_games):
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return fetch_data(min_games=min_games).to_dict('records')
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Map the clicked button to the corresponding role
    role = None
    if button_id == 'btn-top':
        role = 'TOP'
    elif button_id == 'btn-jungle':
        role = 'JUNGLE'
    elif button_id == 'btn-middle':
        role = 'MIDDLE'
    elif button_id == 'btn-bottom':
        role = 'BOTTOM'
    elif button_id == 'btn-support':
        role = 'SUPPORT'

    # Fetch filtered data based on role and minimum games
    filtered_data = fetch_data(role=role, min_games=min_games)
    return filtered_data.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
