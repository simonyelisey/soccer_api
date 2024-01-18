import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_aggregated_goals_plot(data: pd.DataFrame):
    """
    Selected leagues aggregated goals lineplots.
    """
    goals_aggs = (
        data[data["direction"] == "for"]
        .groupby(["league", "season"])["sum_goals"]
        .agg(["mean", "sum"])
        .reset_index()
    )

    fig_sum = go.Figure()
    fig_mean = go.Figure()

    for league in goals_aggs["league"].unique():
        fig_sum.add_trace(
            go.Scatter(
                x=goals_aggs[goals_aggs["league"] == league]["season"],
                y=goals_aggs[goals_aggs["league"] == league]["sum"],
                mode="lines",
                name=league,
            )
        )

        fig_mean.add_trace(
            go.Scatter(
                x=goals_aggs[goals_aggs["league"] == league]["season"],
                y=goals_aggs[goals_aggs["league"] == league]["mean"],
                mode="lines",
                name=league,
            )
        )

    for fig, name in zip([fig_sum, fig_mean], ["Sum", "Mean"]):
        fig.update_layout(
            yaxis_title="goals",
            height=400,
            width=1200,
            plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            title_text=f"{name} of Scored goals through seasons",
        )

    return fig_sum, fig_mean


def create_aggregated_cards_plot(data: pd.DataFrame):
    """
    Selected leagues aggregated goals plots.
    """
    fig_sum = go.Figure()
    fig_mean = go.Figure()

    cards_aggs = (
        data.groupby(["color", "league"])["sum_number"]
        .agg(["mean", "sum"])
        .reset_index()
    )
    cards_aggs["mean"] = cards_aggs["mean"].round(2)

    for card, color in zip(["yellow", "red"], ["#E7E19B", "#E69CA5"]):
        fig_sum.add_trace(
            go.Bar(
                y=cards_aggs[cards_aggs["color"] == card]["league"],
                x=cards_aggs[cards_aggs["color"] == card]["sum"],
                name=card,
                text=[i for i in cards_aggs[cards_aggs["color"] == card]["sum"]],
                orientation="h",
                marker=dict(color=color, line=dict(color="#000000", width=0.75)),
            )
        )

    for card, color in zip(["yellow", "red"], ["#E7E19B", "#E69CA5"]):
        fig_mean.add_trace(
            go.Bar(
                y=cards_aggs[cards_aggs["color"] == card]["league"],
                x=cards_aggs[cards_aggs["color"] == card]["mean"],
                name=card,
                text=[i for i in cards_aggs[cards_aggs["color"] == card]["mean"]],
                orientation="h",
                marker=dict(color=color, line=dict(color="#000000", width=0.75)),
            )
        )

    for fig, name in zip([fig_sum, fig_mean], ["Sum", "Mean"]):
        fig.update_layout(
            yaxis_title="cards",
            height=400,
            width=600,
            plot_bgcolor="white",
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            title_text=f"{name} of cards",
        )

    return fig_sum, fig_mean


def create_aggregated_cleansheets_plot(data: pd.DataFrame):
    """
    Selected leagues aggregated cleansheets plots.
    """
    cs_aggs = data.groupby(["league"])["sum_games"].agg(["mean", "sum"]).reset_index()
    cs_aggs["mean"] = cs_aggs["mean"].round(2)

    fig = px.bar(
        cs_aggs,
        x="league",
        y="sum",
        color="league",
        text_auto=".s",
        title="Sum of Cleansheets",
    )

    fig.update_layout(
        height=400,
        width=1200,
        plot_bgcolor="white",
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
    )

    fig.update_traces(marker=dict(line=dict(color="#000000", width=0.75)))

    return fig
