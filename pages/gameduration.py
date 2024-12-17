import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import database_manager as dbm

# Register the page
dash.register_page(__name__, path="/gameduration", name="Game Duration Stats")

# Fetch data: Group games by duration ranges
def fetch_duration_distribution():
    query = """
        SELECT 
            CASE
                WHEN gameDuration < 900 THEN '0-15 mins'
                WHEN gameDuration BETWEEN 900 AND 1500 THEN '15-25 mins'
                WHEN gameDuration BETWEEN 1500 AND 2100 THEN '25-35 mins'
                WHEN gameDuration BETWEEN 2100 AND 2700 THEN '35-45 mins'
                ELSE '45+ mins'
            END AS duration_range,
            COUNT(*) AS total_games
        FROM match_info
        GROUP BY duration_range
        ORDER BY total_games DESC;
    """
    return dbm.get_data(query)



# Layout for Game Duration Stats
layout = dbc.Container([
    html.H1("Game Duration Statistics", className="text-center mb-4"),
    html.P("An overview of game durations grouped into ranges.", className="text-center"),
    
    # Distribution Pie Chart
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="duration-distribution-chart")
        ], width=12)
    ]),
    
    html.Hr(),
    html.H3("Champion Win Rates by Time Bracket", className="text-center"),

    # Filters and Table
    dbc.Row([
        dbc.Col([
            html.Label("Minimum Games:"),
            dcc.Input(
                id="min-games-input",
                type="number",
                value=1,
                min=0,
                step=1,
                style={"width": "100px"}
            )
        ], width=3, style={"textAlign": "center"}),

        dbc.Col([
            html.Label("Time Bracket:"),
            dcc.Dropdown(
                id="time-bracket-dropdown",
                options=[
                    {"label": "0-15 mins", "value": "0-15 mins"},
                    {"label": "15-25 mins", "value": "15-25 mins"},
                    {"label": "25-35 mins", "value": "25-35 mins"},
                    {"label": "35-45 mins", "value": "35-45 mins"},
                    {"label": "45+ mins", "value": "45+ mins"}
                ],
                value="15-25 mins",
                style={"width": "100%"}
            )
        ], width=3, style={"textAlign": "center"}),

        dbc.Col([
            html.Label("Role:"),
            dcc.Dropdown(
                id="role-filter-dropdown",
                options=[
                    {"label": "All", "value": "ALL"},
                    {"label": "Top", "value": "TOP"},
                    {"label": "Jungle", "value": "JUNGLE"},
                    {"label": "Middle", "value": "MIDDLE"},
                    {"label": "Bottom", "value": "BOTTOM"},
                    {"label": "Utility (Support)", "value": "UTILITY"}
                ],
                value="ALL",
                style={"width": "100%"}
            )
        ], width=3, style={"textAlign": "center"})
    ]),

    html.Div(id="champion-stats-table")
], fluid=True)



# Callback to update the table and pie chart
@callback(
    Output("champion-stats-table", "children"),
    [Input("time-bracket-dropdown", "value"),
     Input("min-games-input", "value"),
     Input("role-filter-dropdown", "value")]
)
def update_champion_stats(time_bracket, min_games, role):
    # SQL query with time bracket and filters
    query = f"""
        SELECT 
            championName, 
            TRIM(individualPosition) AS role,
            COUNT(*) AS total_games,
            100.0 * SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate
        FROM participants
        JOIN match_info ON participants.matchId = match_info.matchId
        WHERE CASE
            WHEN gameDuration < 900 THEN '0-15 mins'
            WHEN gameDuration BETWEEN 900 AND 1500 THEN '15-25 mins'
            WHEN gameDuration BETWEEN 1500 AND 2100 THEN '25-35 mins'
            WHEN gameDuration BETWEEN 2100 AND 2700 THEN '35-45 mins'
            ELSE '45+ mins'
        END = '{time_bracket}'
    """
    if role != "ALL":
        query += f" AND UPPER(individualPosition) = '{role}'"

    query += f"""
        GROUP BY championName, role
        HAVING COUNT(*) >= {min_games}
        ORDER BY total_games DESC;
    """

    data = dbm.get_data(query)

    # Handle no data scenario
    if data.empty:
        return html.Div("No data available for the selected filters.", style={"color": "white", "textAlign": "center"})

    # Build HTML table
    table_rows = [
        html.Tr([
            html.Td(row["championName"]),
            html.Td(html.Img(
                src=f"assets/champion_images/{row['championName']}.png",
                style={"width": "30px", "height": "30px", "objectFit": "contain"}
            )),
            html.Td(row["role"]),
            html.Td(row["total_games"]),
            html.Td(f"{row['win_rate']:.2f}")
        ]) for _, row in data.iterrows()
    ]

    return html.Table(
        # Table headers
        children=[
            html.Thead(html.Tr([
                html.Th("Champion"),
                html.Th("Image"),
                html.Th("Role"),
                html.Th("Total Games"),
                html.Th("Win Rate (%)")
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


import plotly.graph_objects as go

@callback(
    Output("duration-distribution-chart", "figure"),
    Input("time-bracket-dropdown", "value")  # Optional, in case you want filtering
)
def update_duration_chart(_):
    # Fetch the duration data
    query = "SELECT gameDuration FROM match_info;"
    data = dbm.get_data(query)

    # Create the histogram styled to look like a bar chart
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=data["gameDuration"] / 60,  # Convert to minutes
        nbinsx=10,  # Adjust bin count for cleaner appearance
        marker=dict(color="#0F8C82", line=dict(color="#022F3F", width=1)),  # Bar chart color and border
        hoverinfo="x+y",
        showlegend=False
    ))

    # Update layout to match bar chart aesthetic
    fig.update_layout(
        title="Game Duration Distribution (in Minutes)",
        xaxis_title="Game Duration (minutes)",
        yaxis_title="Number of Games",
        plot_bgcolor="#002b36",
        paper_bgcolor="#002b36",
        font=dict(color="white"),
        bargap=0.2  # Add space between bars for cleaner look
    )

    return fig



