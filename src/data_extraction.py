import datetime
import time

import hydra
import pandas as pd
import requests
from omegaconf import DictConfig
from tqdm import tqdm

import database_connection


def extract_available_teams(
    url_teams: str, headers: dict, seasons: list, league_ids: list
):
    """
    Извлечение всех команд, принимавших участие в турнире в заданные сезоны и чемпионаты.

    :param url_teams: str url к странице с информацией о командах на rapid-api
    :param headers: dict конфигурации для подкючения к rapid api:
                        - key
                        - host
    :param seasons: list сезонов
    :param league_ids: list id лиг
    :return: dict
    """
    teams = {}

    for season in seasons:
        teams[season] = {}
        teams[season]["leagues"] = {}

        for league_id in league_ids:
            # get response
            querystring = {"league": league_id, "season": season}
            response_teams = requests.get(
                url_teams, headers=headers, params=querystring
            ).json()

            # save response
            teams[season]["leagues"][league_id] = {
                "id": league_id,
                "teams": response_teams["response"],
            }

    return teams


def extract_cards_statistics(stats: dict) -> pd.DataFrame:
    """
    Извлечение статистики полученных карточек командой за сезон

    :param stats: dict статистики команды

    :return: pd.DataFrame
    """
    colors = []
    minutes = []
    numbers = []

    for color in stats["cards"]:
        for minute in stats["cards"][color]:
            colors.append(color)
            minutes.append(minute)
            numbers.append(stats["cards"][color][minute]["total"])

    cards = pd.DataFrame(
        {
            "color": colors,
            "minute": minutes,
            "number": numbers,
            "team": stats["team"]["name"],
            "league": stats["league"]["name"],
            "season": stats["league"]["season"],
        }
    )

    cards["number"] = cards["number"].fillna(0).astype(int)

    return cards


def extract_lineups_statistics(stats: dict) -> pd.DataFrame:
    """
    Извлечение статистики схемы выхода игровков на поле командой за сезон.

    :param stats: dict статистики команды

    :return: pd.DataFrame
    """
    lineups = pd.DataFrame(
        {
            "formation": [i["formation"] for i in stats["lineups"]],
            "games": [i["played"] for i in stats["lineups"]],
            "team": stats["team"]["name"],
            "league": stats["league"]["name"],
            "season": stats["league"]["season"],
        }
    )

    return lineups


def extract_penalties_statistics(stats: dict) -> pd.DataFrame:
    """
    Извлечение статистики ударов пенальти командой за сезон.

    :param stats: dict статистики команды

    :return: pd.DataFrame
    """
    penalties = pd.DataFrame(
        {
            "number": [
                stats["penalty"]["scored"]["total"],
                stats["penalty"]["missed"]["total"],
            ],
            "result": ["scored", "missed"],
            "team": stats["team"]["name"],
            "league": stats["league"]["name"],
            "season": stats["league"]["season"],
        }
    )

    return penalties


def extract_cleansheets_statistics(stats: dict) -> pd.DataFrame:
    """
    Извлечение статистики проведенных "сухих" матчей командой за сезон.

    :param stats: dict статистики команды

    :return: pd.DataFrame
    """
    clean_sheets = pd.DataFrame(
        {
            "location": list(stats["clean_sheet"].keys()),
            "games": list(stats["clean_sheet"].values()),
            "team": stats["team"]["name"],
            "league": stats["league"]["name"],
            "season": stats["league"]["season"],
        }
    )
    clean_sheets = clean_sheets.iloc[:2, :]

    return clean_sheets


def extract_goals_statistics(stats: dict) -> pd.DataFrame:
    """
    Извлечение статистики забитых мячей командой за сезон.

    :param stats: dict статистики команды

    :return: pd.DataFrame
    """
    minutes_total = []

    for direction in ["for", "against"]:
        minutes = [i for i in stats["goals"][direction]["minute"]]
        minutes_goals = [
            stats["goals"][direction]["minute"][i]["total"]
            for i in stats["goals"][direction]["minute"]
        ]

        minutes_goals_df = pd.DataFrame(
            {
                "minute": minutes,
                "goals": minutes_goals,
                "team": stats["team"]["name"],
                "league": stats["league"]["name"],
                "season": stats["league"]["season"],
                "direction": direction,
            }
        )

        minutes_total.append(minutes_goals_df)

    minutes_total_df = pd.concat(minutes_total).reset_index(drop=True)
    minutes_total_df["goals"] = minutes_total_df["goals"].fillna(0).astype(int)

    return minutes_total_df


def extract_standings(response_standings: dict) -> pd.DataFrame:
    """
    Извлечение турнирных таблиц.

    :param response_standings: dict статистика с турнирной таблицей чемпионатов

    :return: pd.DataFrame
    """
    ranks = []
    teams = []
    points = []
    goals_diff = []
    forms = []
    descriptions = []
    played = []
    wins = []
    draws = []
    loses = []
    scored = []
    missed = []

    standings = response_standings["response"][0]["league"]["standings"][0]

    for i in standings:
        ranks.append(i["rank"])
        teams.append(i["team"]["name"])
        points.append(i["points"])
        goals_diff.append(i["goalsDiff"])
        forms.append(i["form"])
        descriptions.append(i["description"])
        played.append(i["all"]["played"])
        wins.append(i["all"]["win"])
        draws.append(i["all"]["draw"])
        loses.append(i["all"]["lose"])
        scored.append(i["all"]["goals"]["for"])
        missed.append(i["all"]["goals"]["against"])

    summary = pd.DataFrame(
        {
            "season": response_standings["response"][0]["league"]["season"],
            "league": response_standings["response"][0]["league"]["name"],
            "rank": ranks,
            "team": teams,
            "points": points,
            "played": played,
            "win": wins,
            "draw": draws,
            "lose": loses,
            "scored": scored,
            "missed": missed,
            "goals_diff": goals_diff,
            "form": forms,
            "description": descriptions,
        }
    )

    return summary


def extract_top_scorers_statistics(response_top_scorers: dict) -> pd.DataFrame:
    """
    Извлечение статистик топ-игроков.

    :param response_top_scorers: dict статистика топ-игроков

    :return: pd.DataFrame
    """
    league = []
    players = []
    players_teams = []
    ages = []
    nationalities = []
    games_number = []
    minutes_played = []
    scored_goals = []
    assists = []
    shots = []

    top_scorers = response_top_scorers["response"]

    for i in top_scorers:
        league.append(i["statistics"][0]["league"]["name"])
        players.append(i["player"]["name"])
        players_teams.append(i["statistics"][0]["team"]["name"])
        ages.append(i["player"]["age"])
        nationalities.append(i["player"]["nationality"])
        games_number.append(i["statistics"][0]["games"]["appearences"])
        minutes_played.append(i["statistics"][0]["games"]["minutes"])
        scored_goals.append(i["statistics"][0]["goals"]["total"])
        assists.append(i["statistics"][0]["goals"]["assists"])
        shots.append(i["statistics"][0]["shots"]["total"])

    summary = pd.DataFrame(
        {
            "season": int(response_top_scorers["parameters"]["season"]),
            "league": league,
            "player": players,
            "team": players_teams,
            "age": ages,
            "nationality": nationalities,
            "games": games_number,
            "minutes": minutes_played,
            "shots": shots,
            "assists": assists,
            "goals": scored_goals,
        }
    )

    summary["min_per_goal"] = (summary["minutes"] / summary["goals"]).round(2)
    summary["shots_per_goal"] = (summary["shots"] / summary["goals"]).round(2)
    summary["shots"] = summary["shots"].fillna(0).astype(int)
    summary["assists"] = summary["assists"].fillna(0).astype(int)

    return summary


@hydra.main(version_base=None, config_path="../conf", config_name="configs")
def main(cfg: DictConfig):
    """"""
    # rapid api headers
    headers = {
        "X-RapidAPI-Key": cfg["rapid_api"]["key"],
        "X-RapidAPI-Host": cfg["rapid_api"]["host"],
    }

    leagues = cfg["data_extraction"]["leagues"]

    # если первый запуск, то извлекаем всю историю от seasons[0] до seasons[-1]
    if cfg["data_extraction"]["first_run"]:
        seasons = cfg["data_extraction"]["seasons"]
    # если запуск не первый, то извлекаем статистику только за последний сезон
    else:
        seasons = [cfg["data_extraction"]["seasons"][-1]]

    # extract teams
    teams = extract_available_teams(
        url_teams=cfg["urls"]["teams"],
        headers=headers,
        seasons=seasons,
        league_ids=leagues,
    )

    # urls
    url_teams_statistics = cfg["urls"]["teams_statistics"]
    url_standings = cfg["urls"]["standings"]
    url_topscorers = cfg["urls"]["top_scorers"]

    all_standings = []
    all_topscorers = []
    all_cards = []
    all_lineups = []
    all_penalties = []
    all_cleansheets = []
    all_goals = []

    for season in tqdm(seasons):
        for league in leagues:
            # standings & topscorers statistics extraction

            querystring = {"season": season, "league": league}
            response_standings = requests.get(
                url_standings, headers=headers, params=querystring
            ).json()
            response_topscorers = requests.get(
                url_topscorers, headers=headers, params=querystring
            ).json()

            # standigs statistics
            standings = extract_standings(response_standings=response_standings)
            all_standings.append(standings)

            # topscorers statistics
            topscorers = extract_top_scorers_statistics(
                response_top_scorers=response_topscorers
            )
            all_topscorers.append(topscorers)

            # teams statistics extraction
            for team in teams[season]["leagues"][league]["teams"]:
                team_id = team["team"]["id"]

                teams_querystring = {
                    "league": league,
                    "season": season,
                    "team": team_id,
                }
                response_stats = requests.get(
                    url_teams_statistics, headers=headers, params=teams_querystring
                ).json()
                time.sleep(3)
                stats = response_stats["response"]

                # cards statistics
                cards = extract_cards_statistics(stats=stats)
                all_cards.append(cards)

                # lineup statistics
                lineups = extract_lineups_statistics(stats=stats)
                all_lineups.append(lineups)

                # penalties statistics
                penalties = extract_penalties_statistics(stats=stats)
                all_penalties.append(penalties)

                # clean sheets statistics
                clean_sheets = extract_cleansheets_statistics(stats=stats)
                all_cleansheets.append(clean_sheets)

                # goals statistics
                goals_by_minutes = extract_goals_statistics(stats=stats)
                all_goals.append(goals_by_minutes)

    # concat all dataframes
    all_standings = pd.concat(all_standings)
    all_topscorers = pd.concat(all_topscorers)
    all_cards = pd.concat(all_cards)
    all_lineups = pd.concat(all_lineups)
    all_penalties = pd.concat(all_penalties)
    all_cleansheets = pd.concat(all_cleansheets)
    all_goals = pd.concat(all_goals)

    # db connection
    mydb = database_connection.SoccerDatabase(
        host=cfg["db"]["host"],
        database=cfg["db"]["database"],
        user=cfg["db"]["user"],
        password=cfg["db"]["password"],
        port=cfg["db"]["port"],
    )

    for data, name in zip(
        [
            all_standings,
            all_topscorers,
            all_cards,
            all_lineups,
            all_penalties,
            all_cleansheets,
            all_goals,
        ],
        [
            "standings",
            "topscorers",
            "cards",
            "lineups",
            "penalties",
            "cleansheets",
            "goals",
        ],
    ):
        today = datetime.datetime.now()
        data["date_extraction"] = today.date()
        data["time_extraction"] = today

        mydb.write_dataframe(table_name=name, df=data)

    mydb.close()


if __name__ == "__main__":
    main()
