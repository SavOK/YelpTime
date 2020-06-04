from typing import Dict
from sqlalchemy import (
    Column,
    PrimaryKeyConstraint,
)
from sqlalchemy import Sequence
from sqlalchemy.dialects import postgresql as psql

from .base import Base, Session


class Category(Base):
    """
    wrapper to category table
    """

    __tablename__ = "categories"
    category_alias = Column(
        psql.TEXT, nullable=False, quote=False, name="category_alias"
    )
    title = Column(psql.TEXT, nullable=False, quote=False, name="title")
    __table_args__ = (PrimaryKeyConstraint("category_alias", name="pk_category_id"),)

    def __init__(self, entry: Dict, **kwargs):
        self.category_alias = entry["alias"]
        self.title = entry["title"]

    def get_or_create(self, s: Session):
        row = s.query(Category).filter_by(category_alias=self.category_alias).first()
        if row:
            return (row, False)
        s.add(self)
        s.flush()
        return (self, True)
