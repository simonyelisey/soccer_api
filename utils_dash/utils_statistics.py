import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_goals_distribution(data: pd.DataFrame, **args):
    """
    Scored/missed goals distribution
    """
    colors = {
        "for": args["dash"]["colors"]["agressive"],
        "against": args["dash"]["colors"]["soft"],
    }

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]],
        horizontal_spacing=0.001,
        subplot_titles=("by minutes", "total"),
    )

    for direction, name in zip(["for", "against"], ["scored", "missed"]):
        fig.add_trace(
            go.Bar(
                x=data[data["direction"] == direction]["minute"],
                y=data[data["direction"] == direction]["goals"],
                name=name,
                text=data[data["direction"] == direction]["goals"],
                width=0.35,
                marker_color=colors[direction],
            ),
            row=1,
            col=1,
        )

    sum_goals = (
        data.groupby("direction")["goals"].sum().reset_index().sort_values(by=["goals"])
    )

    fig.add_trace(
        go.Pie(
            values=sum_goals["goals"],
            labels=sum_goals["direction"],
            showlegend=False,
            text=sum_goals["goals"],
            marker_colors=list(colors.values())[::-1],
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        xaxis_title="minutes",
        yaxis_title="goals",
        height=400,
        width=1200,
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
        title_text="Scored/missed goals distribution",
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=0.75)))

    return fig


def create_cards_boxplot(data: pd.DataFrame, **args):
    """
    Card distribution visualusation.
    """
    colors = {
        "yellow": args["dash"]["colors"]["agressive"],
        "red": args["dash"]["colors"]["soft"],
    }

    fig = px.bar(
        data,
        x="minute",
        y="number",
        color="color",
        text_auto=".s",
        color_discrete_map=colors,
    )

    fig.update_layout(
        height=400,
        width=600,
        title_text="Cards distribution",
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=0.75)))

    return fig


def create_lineups_boxplot(data: pd.DataFrame, **args):
    """
    Teams lineups distribution visualisation.
    """
    fig = px.bar(data, x="formation", y="games", text_auto=".s")

    fig.update_layout(
        height=400,
        width=600,
        title_text="Lineups distribution",
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )

    fig.update_traces(
        marker_color=args["dash"]["colors"]["agressive"],
        marker=dict(line=dict(color="#000000", width=0.75)),
    )

    return fig


def create_penalties_boxplot(data: pd.DataFrame, **args):
    """
    Penalties results distribution visualisation.
    """
    colors = {
        "missed": args["dash"]["colors"]["agressive"],
        "scored": args["dash"]["colors"]["soft"],
    }

    fig = px.bar(
        data,
        x="result",
        y="number",
        text_auto=".s",
        color="result",
        color_discrete_map=colors,
    )

    fig.update_layout(
        height=400,
        width=600,
        title_text="Penalties distribution",
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )

    fig.update_traces(
        marker_color=args["dash"]["colors"]["soft"],
        marker=dict(line=dict(color="#000000", width=0.75)),
    )

    return fig


def create_cleansheets_boxplot(data: pd.DataFrame, **args):
    """
    Cleansheets distribution visualisation.
    """
    colors = {
        "home": args["dash"]["colors"]["agressive"],
        "away": args["dash"]["colors"]["soft"],
    }

    fig = px.pie(
        data,
        values="games",
        names="location",
        color="location",
        color_discrete_map=colors,
    )

    fig.update_traces(hole=0.5, textposition="inside", textinfo="value+percent")

    fig.update_layout(
        height=400,
        width=600,
        title_text="Cleansheets distribution",
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )
    fig.update_traces(marker=dict(line=dict(color="#000000", width=0.75)))

    return fig
