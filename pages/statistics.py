import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import database_manager as dbm

# Register the page
dash.register_page(__name__, path="/statistics", name="Champion Performance")

# Layout for Champion Performance Table
layout = dbc.Container([
    html.H1("Champion Performance Metrics", className="text-center mb-4"),

    # Filters
    dbc.Row([
        # Minimum Games Filter
        dbc.Col([
            html.Label("Minimum Games:"),
            dcc.Input(
                id="min-games-input",
                type="number",
                value=100,  # Default value
                min=0,
                step=1,
                style={"width": "100%"}
            )
        ], width=2),
        # Role Filter
        dbc.Col([
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
                value="ALL",  # Default value
                style={"width": "100%"}
            )
        ], width=2),
        # Sort By Filter
        dbc.Col([
            html.Label("Sort By:"),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[
                    {"label": "Kills per Game", "value": "avg_kills"},
                    {"label": "Deaths per Game", "value": "avg_deaths"},
                    {"label": "Assists per Game", "value": "avg_assists"},
                    {"label": "Building Damage", "value": "avg_building_damage"},
                    {"label": "Total Games", "value": "total_games"}
                ],
                value="avg_kills",  # Default value
                style={"width": "100%"}
            )
        ], width=2),
        # Search Champion Filter
        dbc.Col([
            html.Label("Search Champion:"),
            dcc.Input(
                id="search-champion-input",
                type="text",
                placeholder="Champion Name...",
                style={"width": "100%"}
            )
        ], width=4)  # Increased width for balance
    ], className="mb-4 align-items-center justify-content-center"),

    # Table Placeholder
    html.Div(id="champion-performance-table")
], fluid=True)

# Callback to update the table based on filters
@dash.callback(
    Output("champion-performance-table", "children"),
    [Input("min-games-input", "value"),
     Input("role-dropdown", "value"),
     Input("metric-dropdown", "value"),
     Input("search-champion-input", "value")]
)
def update_champion_table(min_games, role, metric, search_query):
    # Default value for min_games
    if not min_games:
        min_games = 1

    # Query logic mimicking other pages
    query = f"""
        SELECT 
            championName, 
            UPPER(TRIM(individualPosition)) AS role,
            ROUND(AVG(kills), 2) AS avg_kills,
            ROUND(AVG(deaths), 2) AS avg_deaths,
            ROUND(AVG(assists), 2) AS avg_assists,
            ROUND(AVG(damageDealtToBuildings), 2) AS avg_building_damage,
            COUNT(*) AS total_games
        FROM participants
        WHERE TRIM(individualPosition) IS NOT NULL
            AND TRIM(individualPosition) != ''
    """
    # Apply role filter
    if role != "ALL":
        query += f" AND UPPER(TRIM(individualPosition)) = '{role.upper()}'"

    # Apply search query filter
    if search_query:
        query += f" AND LOWER(championName) LIKE '%{search_query.lower()}%'"

    # Grouping and sorting logic
    query += f"""
        GROUP BY championName, UPPER(TRIM(individualPosition))
        HAVING COUNT(*) >= {min_games}
        ORDER BY {metric} DESC;
    """

    # Fetch data
    data = dbm.get_data(query)

    # Handle empty data
    if data.empty:
        return html.Div("No data available.", style={"color": "white", "textAlign": "center"})

    # Generate table rows
    table_rows = [
        html.Tr([
            html.Td(row["championName"]),
            html.Td(html.Img(
                src=f"assets/champion_images/{row['championName']}.png",
                style={"width": "30px", "height": "30px", "objectFit": "contain"}
            )),
            html.Td(row["role"]),
            html.Td(row["avg_kills"]),
            html.Td(row["avg_deaths"]),
            html.Td(row["avg_assists"]),
            html.Td(row["avg_building_damage"]),
            html.Td(row["total_games"])
        ]) for _, row in data.iterrows()
    ]

    # Create table
    return html.Table(
        children=[
            html.Thead(html.Tr([
                html.Th("Champion"),
                html.Th("Image"),
                html.Th("Role"),
                html.Th("Kills/Game"),
                html.Th("Deaths/Game"),
                html.Th("Assists/Game"),
                html.Th("Building Damage"),
                html.Th("Total Games")
            ])),
            html.Tbody(table_rows)
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "color": "white",
            "textAlign": "center",
            "backgroundColor": "#002b36"
        },
        className="table"
    )
