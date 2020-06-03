from pathlib import Path
import json

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from sqlalchemy import (
    Column,
    Date,
    PrimaryKeyConstraint,
    Sequence,
    ForeignKeyConstraint,
)
from sqlalchemy.dialects import postgresql as psql
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


d = _get_sql_param()

url = URL(**d)

engine = create_engine(url, poolclass=NullPool)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class testtable(Base):
    __tablename__ = "test_table"
    uniprot_id = Column(psql.TEXT, nullable=False, quote=False, name="uniprot_id")
    pfam_id = Column(psql.TEXT, nullable=False, quote=False, name="pfam_id")
    __table_args__ = (
        PrimaryKeyConstraint(
            "uniprot_id", "pfam_id", name="pk_uniprot_pfam_map"
        ),
    )

    def __init__(self, uniprot_id: str, pfam_id: str):
        self.uniprot_id = uniprot_id
        self.pfam_id = pfam_id


Base.metadata.create_all(engine)
T = testtable("AAA", "BBB")
