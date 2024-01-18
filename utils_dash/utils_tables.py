import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_standings_boxplot(data: pd.DataFrame, **args) -> px.bar:
    """
    Scored/missed goals distribution visualisation.
    """
    fig = make_subplots(
        rows=1, cols=1, specs=[[{"type": "bar"}]], horizontal_spacing=0.001
    )

    for direction, color in zip(
        ["scored", "missed"], [args["agressive"], args["soft"]]
    ):
        fig.add_trace(
            go.Bar(
                x=data["team"],
                y=data[direction],
                name=direction,
                text=[i for i in data[direction]],
                marker_color=color,
                width=0.35,
            ),
            row=1,
            col=1,
        )

    fig.update_layout(
        yaxis_title="goals",
        margin=dict(l=10, r=10, t=10),
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )

    return fig


def create_results_boxplot(data: pd.DataFrame, **args) -> px.bar:
    """
    Win/lose distribution visualisation.
    """
    fig = make_subplots(
        rows=1, cols=1, specs=[[{"type": "bar"}]], horizontal_spacing=0.001
    )

    for result, color in zip(["win", "lose"], [args["agressive"], args["soft"]]):
        fig.add_trace(
            go.Bar(
                x=data["team"],
                y=data[result],
                name=result,
                text=[i for i in data[result]],
                marker_color=color,
                width=0.35,
            ),
            row=1,
            col=1,
        )

    fig.update_layout(
        yaxis_title="results",
        margin=dict(l=10, r=10, t=10),
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )

    return fig
