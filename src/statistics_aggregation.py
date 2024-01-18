import os

import hydra
from omegaconf import DictConfig

import database_connection


def aggregate_statistics(
    db_connection: database_connection, seasons: list, cfg: DictConfig
) -> None:
    """
    Aggergate extracted statistics and put them to special tables in DB.

    :param db_connection: database_connection - opened PostgresDB connection
    :param seasons: lisr - selected seasons to aggregate
    :param cfg: DictConfig - configs

    :return: None
    """
    statistics_aggregation_queries_path = cfg["sql"][
        "statistics_aggregation_queries_path"
    ]

    sql_queries = os.listdir(statistics_aggregation_queries_path)

    for file in sql_queries:
        with open(os.path.join(statistics_aggregation_queries_path, file), "r") as f:
            query = f.read()

            # update only selected seasons
            for season in seasons:
                cursor = db_connection.conn.cursor()

                cursor.execute(query, (str(season),))

                db_connection.conn.commit()

                cursor.close()


@hydra.main(version_base=None, config_path="../conf", config_name="configs")
def main(cfg: DictConfig):
    """"""
    # если первый запуск, то извлекаем всю историю от seasons[0] до seasons[-1]
    if cfg["data_extraction"]["first_run"]:
        seasons = cfg["data_extraction"]["seasons"]
    # если запуск не первый, то извлекаем статистику только за последний сезон
    else:
        seasons = [cfg["data_extraction"]["seasons"][-1]]

    # db connection
    mydb = database_connection.SoccerDatabase(
        host=cfg["db"]["host"],
        database=cfg["db"]["database"],
        user=cfg["db"]["user"],
        password=cfg["db"]["password"],
        port=cfg["db"]["port"],
    )

    aggregate_statistics(db_connection=mydb, seasons=seasons, cfg=dict(cfg))

    mydb.close()


if __name__ == "__main__":
    main()
