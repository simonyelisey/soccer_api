import os

import hydra
from omegaconf import DictConfig

import database_connection


@hydra.main(version_base=None, config_path="../conf", config_name="configs")
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

    sql_queries = os.listdir(cfg["sql"]["tables_creation_queries_path"])

    for file in sql_queries:
        if file.split(".")[0] not in mydb.show_tables():
            with open(
                os.path.join(cfg["sql"]["tables_creation_queries_path"], file), "r"
            ) as f:
                q = f.read()

                mydb.create_table(query=q)

    mydb.close()


if __name__ == "__main__":
    main()
