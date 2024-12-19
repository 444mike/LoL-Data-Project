import dash
from dash import dcc, html, Input, Output, callback_context
import database_manager as dbm
import plot_generator as pg
import dash_bootstrap_components as dbc
from dash import State  # Import State for role persistence
import os

# Register the page as "Home"
dash.register_page(__name__, path="/", name="Home")

def fetch_data(role=None, min_games=0):
    query = f"""
        SELECT championName,
               TRIM(individualPosition) AS individualPosition,
               COUNT(*) as total_games,
               100.0 * SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate
        FROM participants
    """
    conditions = []
    if role:
        conditions.append(f"UPPER(individualPosition) = '{role.upper()}'")  # Use individualPosition filter
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " GROUP BY championName, individualPosition"
    query += f" HAVING total_games >= {min_games}"  # Minimum games filter
    query += " ORDER BY win_rate DESC;"

    print("DEBUG: Executing query ->", query)  # Debug query
    data = dbm.get_data(query)
    print("DEBUG: Query returned rows ->", len(data))  # Debug rows count
    return data





# Generate table
def generate_table(data):
    return html.Table(
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "color": "#ddd",
            "margin": "20px auto"
        },
        children=[
            # Header row
            html.Tr([
                html.Th("Champion", style={"padding": "10px", "textAlign": "center", "width": "20%"}),
                html.Th("Image", style={"padding": "10px", "textAlign": "center", "width": "20%"}),
                html.Th("Role", style={"padding": "10px", "textAlign": "center", "width": "15%"}),
                html.Th("Total Games", style={"padding": "10px", "textAlign": "center", "width": "20%"}),
                html.Th("Win Rate (%)", style={"padding": "10px", "textAlign": "center", "width": "25%"}),
            ]),
            # Data rows
            *[
                html.Tr([
                    html.Td(row['championName'], style={"padding": "10px", "textAlign": "center"}),
                    html.Td(html.Img(src=f"assets/champion_images/{row['championName']}.png",
                                     style={"width": "50px", "height": "50px"}),
                            style={"padding": "10px", "textAlign": "center"}),
                    html.Td("Support" if row['individualPosition'] == "UTILITY" else row['individualPosition'],
                            style={"padding": "10px", "textAlign": "center"}),  # Display 'Support'
                    html.Td(row['total_games'], style={"padding": "10px", "textAlign": "center"}),
                    html.Td(f"{row['win_rate']:.2f}", style={"padding": "10px", "textAlign": "center"})
                ]) for _, row in data.iterrows()
            ]
        ]
    )





# Layout
data = fetch_data()
layout = dbc.Container([
    html.H1("League of Legends Dashboard", className="text-center mb-4"),

    # Plot generation section (stays at the top)
    html.Div([
        html.H3("Pick Rate vs Win Rate Analysis", className="text-center"),
        html.Label("Select Role to Generate Plot:", className="d-block text-center mb-2"),
        dbc.ButtonGroup([
            dbc.Button("Top", id="plot-btn-top", color="primary"),
            dbc.Button("Jungle", id="plot-btn-jungle", color="success"),
            dbc.Button("Middle", id="plot-btn-middle", color="info"),
            dbc.Button("Bottom", id="plot-btn-bottom", color="warning"),
            dbc.Button("Support", id="plot-btn-support", color="danger")
        ], className="d-flex justify-content-center mb-4")
    ]),
    html.Div(id="plot-container", className="text-center mb-4"),

    # Filters in a single row
    dbc.Row([
        # Role buttons
        dbc.Col(
            dbc.ButtonGroup([
                dbc.Button("Top", id='btn-top', color="primary"),
                dbc.Button("Jungle", id='btn-jungle', color="success"),
                dbc.Button("Middle", id='btn-middle', color="info"),
                dbc.Button("Bottom", id='btn-bottom', color="warning"),
                dbc.Button("Support", id='btn-support', color="danger"),
            ], className="d-flex justify-content-start"),
            width=6  # Half of the row
        ),
        # Minimum Games input
        dbc.Col(
            html.Div([
                html.Label("Minimum Games:", style={"margin-right": "10px"}),
                dcc.Input(id="min-games-input", type="number", value=0, min=0, style={'width': '100px'})
            ], className="d-flex align-items-center"),
            width=3  # Quarter of the row
        ),
        # Search Champion input
        dbc.Col(
            html.Div([
                html.Label("Search Champion:", style={"margin-right": "10px"}),
                dcc.Input(id="search-input", type="text", placeholder="Champion Name...", style={'width': '200px'})
            ], className="d-flex align-items-center"),
            width=3  # Quarter of the row
        )
    ], className="mb-4"),  # Bottom margin for spacing

    # Table
    html.Div(id="win-rate-table", children=generate_table(data), className="mb-4"),
], fluid=True, style={'backgroundColor': '#333333', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'})



@dash.callback(
    [Output("win-rate-table", "children"), Output("plot-container", "children")],
    [
        Input("btn-top", "n_clicks"),
        Input("btn-jungle", "n_clicks"),
        Input("btn-middle", "n_clicks"),
        Input("btn-bottom", "n_clicks"),
        Input("btn-support", "n_clicks"),
        Input("plot-btn-top", "n_clicks"),
        Input("plot-btn-jungle", "n_clicks"),
        Input("plot-btn-middle", "n_clicks"),
        Input("plot-btn-bottom", "n_clicks"),
        Input("plot-btn-support", "n_clicks"),
        Input("min-games-input", "value"),
        Input("search-input", "value")
    ],
    [State("btn-top", "n_clicks"),
     State("btn-jungle", "n_clicks"),
     State("btn-middle", "n_clicks"),
     State("btn-bottom", "n_clicks"),
     State("btn-support", "n_clicks")]
)
def update_content(n_top, n_jungle, n_middle, n_bottom, n_support,
                   n_plot_top, n_plot_jungle, n_plot_middle, n_plot_bottom, n_plot_support,
                   min_games, search_query,
                   s_top, s_jungle, s_middle, s_bottom, s_support):

    ctx = callback_context
    role = None
    generate_plot = False

    # Check which button triggered the callback
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # Role filter buttons
        if button_id == "btn-top": role = "TOP"
        elif button_id == "btn-jungle": role = "JUNGLE"
        elif button_id == "btn-middle": role = "MIDDLE"
        elif button_id == "btn-bottom": role = "BOTTOM"
        elif button_id == "btn-support": role = "UTILITY"
        # Plot buttons
        elif button_id == "plot-btn-top": role, generate_plot = "TOP", True
        elif button_id == "plot-btn-jungle": role, generate_plot = "JUNGLE", True
        elif button_id == "plot-btn-middle": role, generate_plot = "MIDDLE", True
        elif button_id == "plot-btn-bottom": role, generate_plot = "BOTTOM", True
        elif button_id == "plot-btn-support": role, generate_plot = "UTILITY", True

    # Maintain previously selected role if no role button was clicked
    if role is None:
        if s_top and s_top > 0: role = "TOP"
        elif s_jungle and s_jungle > 0: role = "JUNGLE"
        elif s_middle and s_middle > 0: role = "MIDDLE"
        elif s_bottom and s_bottom > 0: role = "BOTTOM"
        elif s_support and s_support > 0: role = "SUPPORT"

    # Fetch table data
    table_data = fetch_data(role=role, min_games=min_games)
    table = generate_table(table_data)

    # Generate plot if required
    plot = html.Div("")  # Default empty placeholder
    if generate_plot and role:
        plot_path = pg.plot_role_data(role, min_games or 0)
        if os.path.exists(plot_path):
            # Convert the file system path to a web-accessible path
            plot_url = f"/assets/{os.path.basename(plot_path)}"
            plot = html.Img(src=plot_url, style={"width": "80%", "margin-top": "20px"})

    return table, plot



