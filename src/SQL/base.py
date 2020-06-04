from pathlib import Path
import json

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import config
import sys


def _get_sql_param(PROJECT_LOC: Path = Path(config.PROJECT_LOC), ENV: str = config.ENV):
    file_loc = PROJECT_LOC / ".configs"
    file_path = file_loc / "postgres.json"
    if not file_path.is_file():
        raise FileNotFoundError(
            "PostgreSQL sitting file: {} not ther".format(file_path)
        )
    with open(file_path) as oF:
        D = json.load(oF)
    if ENV not in D:
        raise KeyError(f"Enviroment {ENV} not set in {file_path}")
    return D[ENV]


_DB_PAR = _get_sql_param()

url = URL(**_DB_PAR)

engine = create_engine(url, poolclass=NullPool)
Session = sessionmaker(bind=engine)
Base = declarative_base()
