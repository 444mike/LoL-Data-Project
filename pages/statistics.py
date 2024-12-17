import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
import database_manager as dbm

# Register the page
dash.register_page(__name__, path="/statistics", name="Champion Performance")

# Layout for Champion Performance Table
layout = dbc.Container([
    html.H1("Champion Performance Metrics", className="text-center mb-4"),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Minimum Games: "),
            dcc.Input(
                id="min-games-input",
                type="number",
                value=1,  # Default value
                min=0,
                step=1,
                style={"width": "100px"}
            )
        ], width=3),
        dbc.Col([
            html.Label("Role: "),
            dcc.Dropdown(
                id="role-dropdown",
                options=[
                    {"label": "All", "value": "ALL"},
                    {"label": "Top", "value": "TOP"},
                    {"label": "Jungle", "value": "JUNGLE"},
                    {"label": "Middle", "value": "MIDDLE"},
                    {"label": "Bottom", "value": "BOTTOM"},
                    {"label": "Utility (Support)", "value": "UTILITY"}
                ],
                value="ALL",  # Default value
                style={"width": "100%"}
            )
        ], width=3),
        dbc.Col([
            html.Label("Sort By: "),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[
                    {"label": "Kills per Game", "value": "avg_kills"},
                    {"label": "Deaths per Game", "value": "avg_deaths"},
                    {"label": "Assists per Game", "value": "avg_assists"},
                    {"label": "Building Damage", "value": "avg_building_damage"}
                ],
                value="avg_kills",  # Default value
                style={"width": "100%"}
            )
        ], width=3),
    ], className="mb-3"),

    html.Div(id="champion-performance-table")  # Table placeholder
], fluid=True)

# Callback to update the table based on filters
@callback(
    Output("champion-performance-table", "children"),
    [Input("min-games-input", "value"),
     Input("role-dropdown", "value"),
     Input("metric-dropdown", "value")]
)
def update_champion_table(min_games, role, metric):
    # Fallback to 1 if min_games is None
    if not min_games:
        min_games = 1

    # Base query with role cleaning
    query = f"""
        SELECT 
            championName, 
            CASE 
                WHEN UPPER(TRIM(individualPosition)) IN ('TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY') 
                    THEN UPPER(TRIM(individualPosition))
                ELSE 'UNKNOWN'
            END AS role,
            ROUND(AVG(kills), 2) AS avg_kills,
            ROUND(AVG(deaths), 2) AS avg_deaths,
            ROUND(AVG(assists), 2) AS avg_assists,
            ROUND(AVG(damageDealtToBuildings), 2) AS avg_building_damage,
            COUNT(*) AS total_games
        FROM participants
        WHERE TRIM(individualPosition) IS NOT NULL AND TRIM(individualPosition) != ''
    """
    # Role filter
    if role != "ALL":
        query += f" AND UPPER(TRIM(individualPosition)) = '{role}'"

    # Grouping, filtering, and sorting
    query += f"""
        GROUP BY championName, role
        HAVING COUNT(*) >= {min_games}
        ORDER BY {metric} DESC;
    """

    # Fetch data
    data = dbm.get_data(query)

    # Debug: Print unique roles fetched
    print("Roles fetched from database:", data['role'].unique())

    # Add image links to the data
    data['image'] = data['championName'].apply(
        lambda name: f'<img src="assets/champion_images/{name}.png" width="40" height="40" style="vertical-align: middle;">'
    )

    # Return table with images
    return dash_table.DataTable(
        id="performance-table",
        columns=[
            {"name": "Champion", "id": "championName"},
            {"name": "Image", "id": "image", "presentation": "markdown"},
            {"name": "Role", "id": "role"},
            {"name": "Kills per Game", "id": "avg_kills"},
            {"name": "Deaths per Game", "id": "avg_deaths"},
            {"name": "Assists per Game", "id": "avg_assists"},
            {"name": "Building Damage", "id": "avg_building_damage"},
            {"name": "Number of Games", "id": "total_games"}
        ],
        data=data.to_dict('records'),
        markdown_options={"html": True},  # Enable HTML for inline image resizing
        style_header={
            "backgroundColor": "#444",
            "color": "white",
            "fontWeight": "bold"
        },
        style_data={
            "backgroundColor": "#222",
            "color": "white",
            "textAlign": "center",
            "fontSize": "12px"  # Optional: Reduce font size for compactness
        },
        style_data_conditional=[
            {"if": {"column_id": "image"}, "width": "40px", "padding": "5px"}  # Image column adjustments
        ],
        style_table={"overflowX": "auto"},
        sort_action="native"
    )
