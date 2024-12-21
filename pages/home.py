import dash
from dash import dcc, html, Input, Output, callback_context
import database_manager as dbm
import plot_generator as pg
import dash_bootstrap_components as dbc
import os

# Register the page as "Home"
dash.register_page(__name__, path="/", name="Home")


def fetch_data(role=None, min_games=0, search_query=None, sort_by="win_rate"):
    query = f"""
        SELECT championName, 
               TRIM(individualPosition) AS individualPosition, 
               COUNT(*) as total_games,
               100.0 * SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate,
               100.0 * COUNT(*) / (SELECT COUNT(*) FROM participants) AS pick_rate
        FROM participants
    """
    conditions = []
    if role:
        conditions.append(f"UPPER(individualPosition) = '{role.upper()}'")
    if search_query:
        conditions.append(f"LOWER(championName) LIKE '%{search_query.lower()}%'")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " GROUP BY championName, individualPosition"
    query += f" HAVING total_games >= {min_games}"
    query += f" ORDER BY {sort_by} DESC;"
    data = dbm.get_data(query)
    return data


def generate_table(data):
    if data.empty:
        return html.Div("No data available.", style={"color": "white", "textAlign": "center"})

    role_mapping = {
        "TOP": "Top",
        "JUNGLE": "Jungle",
        "MIDDLE": "Mid",
        "BOTTOM": "Bottom",
        "UTILITY": "Support"
    }

    table_rows = [
        html.Tr([
            html.Td(row["championName"]),
            html.Td(html.Img(
                src=f"assets/champion_images/{row['championName']}.png",
                style={"width": "30px", "height": "30px", "objectFit": "contain"}
            )),
            html.Td(role_mapping.get(row["individualPosition"], "Unknown")),
            html.Td(f"{row['win_rate']:.2f}"),
            html.Td(f"{row['pick_rate']:.2f}"),
            html.Td(row["total_games"])
        ]) for _, row in data.iterrows()
    ]

    return html.Table(
        children=[
            html.Thead(html.Tr([
                html.Th("Champion"),
                html.Th("Image"),
                html.Th("Role"),
                html.Th("Win Rate (%)"),
                html.Th("Pick Rate (%)"),
                html.Th("Total Games")
            ])),
            html.Tbody(table_rows)
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "color": "white",
            "textAlign": "center",
            "backgroundColor": "#222"
        },
        className="table"
    )


# Layout
data = fetch_data()
layout = dbc.Container([
    html.H1("League of Legends Dashboard", className="text-center mb-4"),

    # Plot buttons
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

    # Filters in a single row with even spacing
    dbc.Row([
        dbc.Col(html.Div([
            html.Label("Role:"),
            dcc.Dropdown(
                id="role-dropdown",
                options=[
                    {"label": "All", "value": "ALL"},
                    {"label": "Top", "value": "TOP"},
                    {"label": "Jungle", "value": "JUNGLE"},
                    {"label": "Middle", "value": "MIDDLE"},
                    {"label": "Bottom", "value": "BOTTOM"},
                    {"label": "Support", "value": "UTILITY"}
                ],
                value="ALL",
                style={"width": "100%"}
            )
        ]), width=2),
        dbc.Col(html.Div([
            html.Label("Minimum Games:"),
            dcc.Input(id="min-games-input", type="number", value=100, min=0, style={'width': '100%'})
        ]), width=2),
        dbc.Col(html.Div([
            html.Label("Sort By:"),
            dcc.Dropdown(
                id="sort-by-dropdown",
                options=[
                    {"label": "Win Rate (%)", "value": "win_rate"},
                    {"label": "Total Games", "value": "total_games"},
                    {"label": "Pick Rate (%)", "value": "pick_rate"}
                ],
                value="win_rate",
                style={"width": "100%"}
            )
        ]), width=2),
        dbc.Col(html.Div([
            html.Label("Search Champion:"),
            dcc.Input(id="search-input", type="text", placeholder="Champion Name...", style={'width': '100%'})
        ]), width=6)
    ], className="mb-4 align-items-center"),

    # Table
    html.Div(id="win-rate-table", children=generate_table(data), className="mb-4"),
], fluid=True, style={'backgroundColor': '#002b36', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'})


@dash.callback(
    [Output("win-rate-table", "children"), Output("plot-container", "children")],
    [
        Input("role-dropdown", "value"),
        Input("plot-btn-top", "n_clicks"),
        Input("plot-btn-jungle", "n_clicks"),
        Input("plot-btn-middle", "n_clicks"),
        Input("plot-btn-bottom", "n_clicks"),
        Input("plot-btn-support", "n_clicks"),
        Input("min-games-input", "value"),
        Input("search-input", "value"),
        Input("sort-by-dropdown", "value")
    ]
)
def update_content(role, n_plot_top, n_plot_jungle, n_plot_middle, n_plot_bottom, n_plot_support, min_games, search_query, sort_by):
    ctx = callback_context
    generate_plot = False

    # Check which button triggered the callback
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "plot-btn-top": role, generate_plot = "TOP", True
        elif button_id == "plot-btn-jungle": role, generate_plot = "JUNGLE", True
        elif button_id == "plot-btn-middle": role, generate_plot = "MIDDLE", True
        elif button_id == "plot-btn-bottom": role, generate_plot = "BOTTOM", True
        elif button_id == "plot-btn-support": role, generate_plot = "UTILITY", True

    # Fetch table data
    if role == "ALL":
        role = None
    table_data = fetch_data(role=role, min_games=min_games, search_query=search_query, sort_by=sort_by)
    table = generate_table(table_data)

    # Generate plot if required
    plot = html.Div("")
    if generate_plot and role:
        plot_path = pg.plot_role_data(role, min_games or 0)
        if os.path.exists(plot_path):
            plot = html.Img(src=plot_path, style={"width": "50%", "margin-top": "20px"})  # Adjusted plot size

    return table, plot
