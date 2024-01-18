import pandas as pd
import plotly.graph_objects as go


def create_barplot(data: pd.DataFrame, column: str, team: str, horizontal=False):
    """
    Selected team column boxplot.

    params:
        data - statistics dataframe
        column - values
        team - name of team
        horizontal - whether to plot barplot in horizontal orientation
    """
    if horizontal:
        if team in data["team"].unique():
            fig = go.Bar(
                y=data["team"],
                x=data[column],
                name=team,
                text=[i for i in data[column]],
                orientation="h",
            )
        else:
            fig = go.Bar(
                y=[f"{team} is relegated."],
                x=[0],
                name=team,
                text=["relegated"],
                orientation="h",
            )
    else:
        if team in data["team"].unique():
            fig = go.Bar(
                x=data["team"],
                y=data[column],
                name=team,
                text=[i for i in data[column]],
            )
        else:
            fig = go.Bar(
                x=[f"{team} is relegated."], y=[0], name=team, text=["relegated"]
            )

    return fig
