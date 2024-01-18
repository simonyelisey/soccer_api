import dash_bootstrap_components as dbc
import hydra
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback
from dash import dash_table as dt
from dash import dcc, html
from omegaconf import DictConfig
from plotly.subplots import make_subplots

import src.database_connection as database_connection
from utils_dash.utils_aggregations import (create_aggregated_cards_plot,
                                           create_aggregated_cleansheets_plot,
                                           create_aggregated_goals_plot)
from utils_dash.utils_h2h import create_barplot
from utils_dash.utils_statistics import (create_cards_boxplot,
                                         create_cleansheets_boxplot,
                                         create_goals_distribution,
                                         create_lineups_boxplot,
                                         create_penalties_boxplot)
from utils_dash.utils_tables import (create_results_boxplot,
                                     create_standings_boxplot)


def filter_max_date(data: pd.DataFrame) -> pd.DataFrame:
    """
    Фильтрация данных по максимальной дате экстракции статистики.

    :param data: pd.DataFrame со статистикой

    :return: pd.DataFrame
    """
    max_date = data.groupby(["season"])["time_extraction"].max().reset_index()

    data = data.merge(max_date, on=["season", "time_extraction"]).reset_index(drop=True)

    return data


def get_data(table_name, db_connection):
    """"""
    data = db_connection.query(
        f"""
        select * from {table_name}
        """
    )

    return data


@hydra.main(version_base=None, config_path="./conf", config_name="configs")
def main(cfg: DictConfig):
    """"""
    # db connection
    mydb = database_connection.SoccerDatabase(
        host=cfg["db"]["host"],
        database=cfg["db"]["database"],
        user=cfg["db"]["user"],
        password=cfg["db"]["password"],
        port=cfg["db"]["port"],
    )

    # get data
    standings = get_data(table_name="standings", db_connection=mydb)
    topscorers = get_data(table_name="topscorers", db_connection=mydb)
    cards = get_data(table_name="cards", db_connection=mydb)
    goals_distribution = get_data(table_name="goals", db_connection=mydb)
    lineups = get_data(table_name="lineups", db_connection=mydb)
    penalties = get_data(table_name="penalties", db_connection=mydb)
    cleansheets = get_data(table_name="cleansheets", db_connection=mydb)
    # aggregations
    cards_aggregations = get_data(table_name="cards_aggregations", db_connection=mydb)
    cleansheets_aggregations = get_data(
        table_name="cleansheets_aggregations", db_connection=mydb
    )
    goals_aggregations = get_data(table_name="goals_aggregations", db_connection=mydb)

    # keep only max date of data extraction for each season
    standings = filter_max_date(data=standings).drop(
        cfg["dash"]["redundant_columns"] + ["description"], axis=1
    )
    topscorers = filter_max_date(data=topscorers).drop(
        cfg["dash"]["redundant_columns"], axis=1
    )
    cards = filter_max_date(data=cards).drop(cfg["dash"]["redundant_columns"], axis=1)
    goals_distribution = filter_max_date(data=goals_distribution).drop(
        cfg["dash"]["redundant_columns"], axis=1
    )
    lineups = filter_max_date(data=lineups).drop(
        cfg["dash"]["redundant_columns"], axis=1
    )
    penalties = filter_max_date(data=penalties).drop(
        cfg["dash"]["redundant_columns"], axis=1
    )
    cleansheets = filter_max_date(data=cleansheets).drop(
        cfg["dash"]["redundant_columns"], axis=1
    )
    # aggregations
    redundant_columns = list(
        set(cfg["dash"]["redundant_columns"]) - set(["date_extraction"])
    )
    cards_aggregations = filter_max_date(data=cards_aggregations).drop(
        redundant_columns, axis=1
    )
    cleansheets_aggregations = filter_max_date(data=cleansheets_aggregations).drop(
        redundant_columns, axis=1
    )
    goals_aggregations = filter_max_date(data=goals_aggregations).drop(
        redundant_columns, axis=1
    )

    mydb.close()

    # available seasons and leagues
    seasons = standings["season"].unique().tolist()
    leagues = standings["league"].unique().tolist()

    app = Dash(suppress_callback_exceptions=True)

    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 110,
        "left": 10,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "background-color": "#EBF5FB",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    sidebar = html.Div(
        children=[
            html.H2("Menu", className="display-4"),
            html.Hr(),
            html.P("Navigation", className="lead"),
            dbc.Nav(
                [
                    dbc.NavLink("Tables", href="/", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
            dbc.Nav(
                [
                    dbc.NavLink("Statistics", href="/page-1", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
            dbc.Nav(
                [dbc.NavLink("H2H", href="/page-2", active="exact")],
                vertical=True,
                pills=True,
            ),
            dbc.Nav(
                [dbc.NavLink("Leagues", href="/page-3", active="exact")],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )

    # head of main page
    head = html.Div(
        style={
            "textAlign": "center",
            "backgroundColor": cfg["dash"]["colors"]["head_background"],
        },
        children=[
            html.H1(children="⚽ Top-5 football leagues statistics ⚽"),
            dcc.Markdown(
                children=cfg["dash"]["markdown_text"], style={"textAlign": "center"}
            ),
        ],
    )

    dropdown_seasons = html.Div(
        [
            "Season",
            dcc.Dropdown(
                id="filter_seasons",
                options=[{"label": ss, "value": ss} for ss in seasons],
                placeholder="Select Season",
                multi=False,
                value=seasons[-1],
            ),
        ]
    )

    dropdown_leagues = html.Div(
        [
            "League",
            dcc.Dropdown(
                id="filter_leagues",
                options=[{"label": league, "value": league} for league in leagues],
                placeholder="Select League",
                multi=False,
                value=leagues[2],
            ),
        ]
    )

    dropdown_teams = html.Div(
        [
            "Team",
            dcc.Dropdown(id="filter_teams", placeholder="Select Team", multi=False),
        ]
    )
    dropdown_multiple_teams = html.Div(
        [
            "Teams",
            dcc.Dropdown(
                id="filter_multiple_teams", placeholder="Select Teams", multi=True
            ),
        ]
    )
    dropdown_multiple_leagues = html.Div(
        [
            "Leagues",
            dcc.Dropdown(
                id="filter_multiple_leagues",
                placeholder="Select Leagues",
                multi=True,
                options=[{"label": league, "value": league} for league in leagues],
            ),
        ]
    )

    # standings & topscorers
    tables = html.Div(
        children=[
            dcc.Markdown(children="# Tables"),
            dcc.Markdown("### Standigs and Topscorers by leagues and seasons."),
            dcc.Markdown(children="*Select Season and League*"),
            dropdown_seasons,
            dropdown_leagues,
            dcc.Markdown(children="\n## Teams Standings"),
            dt.DataTable(
                id="table-standings",
                columns=[
                    {"name": col, "id": col, "deletable": True}
                    for col in standings.columns
                ],
                data=standings.to_dict("records"),
                filter_action="native",
                sort_action="native",
                row_deletable=True,
                page_action="native",
                page_current=0,
                page_size=10,
                style_as_list_view=True,
                style_header={"fontWeight": "bold"},
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{points} > 0", "column_id": "points"},
                        "color": "tomato",
                        "fontWeight": "bold",
                    }
                ],
            ),
            dcc.Graph(id="display_standings", style={"height": 250}),
            dcc.Graph(id="display_results", style={"height": 250}),
            dcc.Markdown(children="\n## Top Scorers"),
            dt.DataTable(
                id="table-topscorers",
                columns=[
                    {"name": col, "id": col, "deletable": True}
                    for col in topscorers.columns
                ],
                data=topscorers.to_dict("records"),
                filter_action="native",
                sort_action="native",
                row_deletable=True,
                page_action="native",
                page_current=0,
                page_size=10,
                style_as_list_view=True,
                style_header={"fontWeight": "bold"},
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{goals} > 0", "column_id": "goals"},
                        "color": "tomato",
                        "fontWeight": "bold",
                    }
                ],
            ),
            html.Div(id="display_topscorers"),
        ]
    )

    # STATISTICS

    goals_distribution_graph = dcc.Graph(id="display_goals_distribution")

    cleansheets_graph = html.Div(
        children=[dcc.Graph(id="display_cleansheets")],
        style={"display": "inline-block"},
    )
    penalties_graph = html.Div(
        children=[dcc.Graph(id="display_penalties")], style={"display": "inline-block"}
    )
    cards_grapth = html.Div(
        children=[dcc.Graph(id="display_cards")], style={"display": "inline-block"}
    )
    lineups_graph = html.Div(
        children=[dcc.Graph(id="display_lineups")], style={"display": "inline-block"}
    )

    page_statistics = html.Div(
        children=[
            dcc.Markdown(children="# Statistics"),
            dcc.Markdown(children="### Statistics of individual teams by seasons"),
            dcc.Markdown(children="*Select Season, League & Team*"),
            dropdown_seasons,
            dropdown_leagues,
            dropdown_teams,
            goals_distribution_graph,
            html.Hr(),
            html.Div(children=[cards_grapth, lineups_graph]),
            html.Hr(),
            html.Div(children=[cleansheets_graph, penalties_graph]),
        ]
    )

    # H2H

    comparison_points = dcc.Graph(id="display_comparison_points")
    slider_seasons = html.Div(
        children=[
            html.Label("Season"),
            dcc.Slider(
                cards["season"].min(),
                cards["season"].max(),
                step=None,
                value=cards["season"].max(),
                marks={str(year): str(year) for year in cards["season"].unique()},
                id="slider_seasons",
            ),
        ]
    )
    comparison_results = dbc.Row([dcc.Graph(id="display_comparison_results")])
    comparison_goals = dbc.Row([dcc.Graph(id="display_comparison_goals")])
    comparison_cards = dbc.Row([dcc.Graph(id="display_comparison_cards")])

    page_h2h = html.Div(
        children=[
            dcc.Markdown(children="# Head to Head Statistics"),
            dcc.Markdown(children="### Statistics comparison of multiple teams"),
            dcc.Markdown(children="*Select League, Teams & Season*"),
            dropdown_leagues,
            dropdown_multiple_teams,
            slider_seasons,
            comparison_results,
            comparison_points,
            comparison_goals,
            comparison_cards,
        ]
    )

    # LEAGUES AGGREGATIONS

    goals_aggregations_graph_sum = dcc.Graph(id="display_goals_aggregations_graph_sum")
    goals_aggregations_graph_mean = dcc.Graph(
        id="display_goals_aggregations_graph_mean"
    )
    cards_aggregations_graph_sum = html.Div(
        children=[dcc.Graph(id="display_cards_aggregations_graph_sum")],
        style={"display": "inline-block"},
    )
    cards_aggregations_graph_mean = html.Div(
        children=[dcc.Graph(id="display_cards_aggregations_graph_mean")],
        style={"display": "inline-block"},
    )
    cleansheets_aggregations_graph = html.Div(
        children=[dcc.Graph(id="display_cleansheets_aggregations_graph")],
        style={"display": "inline-block"},
    )

    # dcc.Graph(id="display_cleansheets_aggregations_graph")

    page_leagues = html.Div(
        children=[
            dcc.Markdown(children="# Leagues Aggregated Statistics"),
            dcc.Markdown(
                children="### Multiple leagues aggregated statistics comparison"
            ),
            dcc.Markdown(children="*Select Leagues & Season*"),
            dropdown_multiple_leagues,
            goals_aggregations_graph_sum,
            goals_aggregations_graph_mean,
            html.Hr(),
            slider_seasons,
            html.Div(
                children=[cards_aggregations_graph_sum, cards_aggregations_graph_mean]
            ),
            cleansheets_aggregations_graph,
        ]
    )

    content = html.Div(id="page-content", style=CONTENT_STYLE)

    app.layout = html.Div(children=[dcc.Location(id="url"), head, sidebar, content])

    # STANDINGS

    # table

    @callback(
        Output("table-standings", "data"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
    )
    def display_standings(season, league):
        dff = standings[
            (standings["season"].isin([season])) & (standings["league"].isin([league]))
        ]

        return dff.to_dict("records")

    # scored/missed goals

    @callback(
        Output("display_standings", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
    )
    def visualize_standings(season, league):
        dff = standings[
            (standings["season"].isin([season])) & (standings["league"].isin([league]))
        ].reset_index(drop=True)

        fig = create_standings_boxplot(data=dff, **cfg["dash"]["colors"])

        return fig

    # win/lose

    @callback(
        Output("display_results", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
    )
    def visualize_results(season, league):
        dff = standings[
            (standings["season"].isin([season])) & (standings["league"].isin([league]))
        ].reset_index(drop=True)

        fig = create_results_boxplot(data=dff, **cfg["dash"]["colors"])

        return fig

    # TOPSCORERS

    @callback(
        Output("table-topscorers", "data"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
    )
    def display_topscorers_table(season, league):
        dff = topscorers[
            (topscorers["season"].isin([season]))
            & (topscorers["league"].isin([league]))
        ]

        return dff.to_dict("records")

    # barplots

    @callback(
        Output("display_topscorers", "children"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
    )
    def display_topscorers(season, league):
        dff = topscorers[
            (topscorers["season"].isin([season]))
            & (topscorers["league"].isin([league]))
        ]

        return [
            dcc.Graph(
                figure={
                    "data": [
                        {
                            "x": dff["player"],
                            "y": dff[column],
                            "type": "bar",
                            "marker": {"color": cfg["dash"]["colors"]["agressive"]},
                            "width": 0.3,
                            "text": [np.round(i, 2) for i in dff[column].unique()],
                        }
                    ],
                    "layout": {
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True, "title": {"text": column}},
                        "height": 250,
                        "margin": {"t": 10, "l": 10, "r": 10},
                    },
                },
            )
            for column in ["min_per_goal", "shots_per_goal"]
            if column in dff
        ]

    # STATISTICS callbacks

    @callback(
        Output("filter_teams", "options"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
    )
    def set_teams_options(season, league):
        dff = cards[(cards["season"].isin([season])) & (cards["league"].isin([league]))]
        available_teams = dff["team"].unique().tolist()

        return [{"label": i, "value": i} for i in available_teams]

    # cards

    @callback(
        Output("display_cards", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_teams", "value"),
    )
    def visualise_cards(season, league, team):
        dff = cards[
            (cards["season"].isin([season]))
            & (cards["league"].isin([league]))
            & (cards["team"].isin([team]))
        ]

        fig = create_cards_boxplot(data=dff, **cfg)

        return fig

    # goals distribution

    @callback(
        Output("display_goals_distribution", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_teams", "value"),
    )
    def visualise_goals_distribution(season, league, team):
        dff = goals_distribution[
            (goals_distribution["season"].isin([season]))
            & (goals_distribution["league"].isin([league]))
            & (goals_distribution["team"].isin([team]))
        ]

        fig = create_goals_distribution(data=dff, **cfg)

        return fig

    # lineups distribution

    @callback(
        Output("display_lineups", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_teams", "value"),
    )
    def visualise_lineups(season, league, team):
        fig = go.Figure()

        if team:
            dff = lineups[
                (lineups["season"].isin([season]))
                & (lineups["league"].isin([league]))
                & (lineups["team"].isin([team]))
            ]

            fig = create_lineups_boxplot(data=dff, **cfg)

            return fig
        else:
            return fig

    # penalties distribution

    @callback(
        Output("display_penalties", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_teams", "value"),
    )
    def visualise_penalties(season, league, team):
        fig = go.Figure()

        if team:
            dff = penalties[
                (penalties["season"].isin([season]))
                & (penalties["league"].isin([league]))
                & (penalties["team"].isin([team]))
            ]

            fig = create_penalties_boxplot(data=dff, **cfg)

            return fig
        else:
            return fig

    # cleansheets distribution

    @callback(
        Output("display_cleansheets", "figure"),
        Input("filter_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_teams", "value"),
    )
    def visualise_cleansheets(season, league, team):
        dff = cleansheets[
            (cleansheets["season"].isin([season]))
            & (cleansheets["league"].isin([league]))
            & (cleansheets["team"].isin([team]))
        ]

        fig = create_cleansheets_boxplot(data=dff, **cfg)

        return fig

    # H2H callbacks

    @callback(
        Output("filter_multiple_teams", "options"), Input("filter_leagues", "value")
    )
    def set_h2h_teams_options(league):
        dff = cards[(cards["league"].isin([league]))]
        available_teams = dff["team"].unique().tolist()

        return [{"label": i, "value": i} for i in available_teams]

    # points

    @callback(
        Output("display_comparison_points", "figure"),
        [
            Input("slider_seasons", "value"),
            Input("filter_leagues", "value"),
            Input("filter_multiple_teams", "value"),
        ],
    )
    def visualise_comparison_points(season, league, teams):
        fig_points = make_subplots(
            rows=1, cols=1, specs=[[{"type": "bar"}]], horizontal_spacing=0.001
        )

        if teams:
            for team in teams:
                dff_standings = standings[
                    (standings["season"].isin([season]))
                    & (standings["league"].isin([league]))
                    & (standings["team"].isin([team]))
                ]

                fig_points.add_trace(
                    create_barplot(data=dff_standings, column="points", team=team)
                )

        fig_points.update_layout(
            yaxis_title="points",
            plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            title_text="Points comparison",
        )

        fig_points.update_traces(marker=dict(line=dict(color="#000000", width=0.75)))

        return fig_points

    # results comparison

    @callback(
        Output("display_comparison_results", "figure"),
        Input("slider_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_multiple_teams", "value"),
    )
    def visualise_comparison_results(season, league, teams):
        fig_results = go.Figure()

        if teams:
            dff_standings = standings[
                (standings["season"].isin([season]))
                & (standings["league"].isin([league]))
                & (standings["team"].isin(teams))
            ]

            for column, color in zip(
                ["win", "draw", "lose"], ["#7BD190", "#E7E19B", "#E69CA5 "]
            ):
                fig_results.add_trace(
                    go.Bar(
                        y=dff_standings["team"],
                        x=dff_standings[column],
                        name=column,
                        text=[i for i in dff_standings[column]],
                        orientation="h",
                        marker=dict(
                            color=color, line=dict(color="#000000", width=0.75)
                        ),
                    )
                )

        fig_results.update_layout(
            yaxis_title="teams",
            plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            title_text="Results comparison",
            barmode="stack",
        )

        return fig_results

    # goals comparison

    @callback(
        Output("display_comparison_goals", "figure"),
        [
            Input("slider_seasons", "value"),
            Input("filter_leagues", "value"),
            Input("filter_multiple_teams", "value"),
        ],
    )
    def visualise_comparison_goals(season, league, teams):
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "pie"}, {"type": "pie"}]],
            horizontal_spacing=0.001,
            subplot_titles=("scored", "missed"),
        )

        if teams:
            dff_goals = goals_distribution[
                (goals_distribution["season"].isin([season]))
                & (goals_distribution["league"].isin([league]))
                & (goals_distribution["team"].isin(teams))
            ]
            goals_sum = (
                dff_goals.groupby(["direction", "team"])["goals"].sum().reset_index()
            )

            for direction, col in zip(["for", "against"], [1, 2]):
                fig.add_trace(
                    go.Pie(
                        labels=goals_sum[goals_sum["direction"] == direction]["team"],
                        values=goals_sum[goals_sum["direction"] == direction]["goals"],
                        name=str(direction),
                    ),
                    row=1,
                    col=col,
                )
        fig.update_traces(
            hole=0.5,
            textposition="inside",
            textinfo="value+percent",
            marker=dict(line=dict(color="#000000", width=0.75)),
        )

        fig.update_layout(
            yaxis_title="teams",
            plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            title_text="Goals comparison",
        )

        return fig

    # cards comparison

    @callback(
        Output("display_comparison_cards", "figure"),
        Input("slider_seasons", "value"),
        Input("filter_leagues", "value"),
        Input("filter_multiple_teams", "value"),
    )
    def visualise_comparison_cards(season, league, teams):
        fig = go.Figure()

        if teams:
            dff = cards[
                (cards["season"].isin([season]))
                & (cards["league"].isin([league]))
                & (cards["team"].isin(teams))
            ]

            cards_sum = dff.groupby(["color", "team"])["number"].sum().reset_index()

            for card, color in zip(["yellow", "red"], ["#E7E19B", "#E69CA5"]):
                fig.add_trace(
                    go.Bar(
                        y=cards_sum[cards_sum["color"] == card]["team"],
                        x=cards_sum[cards_sum["color"] == card]["number"],
                        name=card,
                        text=[
                            i for i in cards_sum[cards_sum["color"] == card]["number"]
                        ],
                        orientation="h",
                        marker=dict(
                            color=color, line=dict(color="#000000", width=0.75)
                        ),
                    )
                )

        fig.update_layout(
            yaxis_title="teams",
            plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            title_text="Cards comparison",
            barmode="stack",
        )

        return fig

    # LEAGUES callbacks

    # goals

    @callback(
        Output("display_goals_aggregations_graph_sum", "figure"),
        Output("display_goals_aggregations_graph_mean", "figure"),
        [Input("filter_multiple_leagues", "value")],
    )
    def visualise_aggregated_goals(leagues):
        fig = go.Figure()

        if leagues:
            dff = goals_aggregations[(goals_aggregations["league"].isin(leagues))]

            fig_sum, fig_mean = create_aggregated_goals_plot(dff)

            return [fig_sum, fig_mean]

        else:
            return [fig, fig]

    # cards

    @callback(
        Output("display_cards_aggregations_graph_sum", "figure"),
        Output("display_cards_aggregations_graph_mean", "figure"),
        [Input("filter_multiple_leagues", "value"), Input("slider_seasons", "value")],
    )
    def visualise_aggregated_cards(leagues, season):
        fig = go.Figure()

        if leagues:
            dff = cards_aggregations[
                (cards_aggregations["league"].isin(leagues))
                & (cards_aggregations["season"] == season)
            ]

            fig_sum, fig_mean = create_aggregated_cards_plot(dff)

            return [fig_sum, fig_mean]

        else:
            return [fig, fig]

    # cleansheets

    @callback(
        Output("display_cleansheets_aggregations_graph", "figure"),
        [Input("filter_multiple_leagues", "value"), Input("slider_seasons", "value")],
    )
    def visualise_aggregated_cleansheets(leagues, season):
        fig = go.Figure()

        if leagues:
            dff = cleansheets_aggregations[
                (cleansheets_aggregations["league"].isin(leagues))
                & (cleansheets_aggregations["season"] == season)
            ]

            fig = create_aggregated_cleansheets_plot(dff)

            return fig
        else:
            return fig

    # NAVIGATION

    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page_content(pathname):
        if pathname == "/":
            return html.Div(children=[tables])
        elif pathname == "/page-1":
            return html.Div(children=[page_statistics])
        elif pathname == "/page-2":
            return html.Div(children=[page_h2h])
        elif pathname == "/page-3":
            return html.Div(children=[page_leagues])

        # If the user tries to reach a different page, return a 404 message
        return html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ],
            className="p-3 bg-light rounded-3",
        )

    app.run_server(debug=True, host="0.0.0.0", port="8050")


if __name__ == "__main__":
    main()
