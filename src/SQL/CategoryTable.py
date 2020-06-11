from typing import Dict
from sqlalchemy import (
    Column,
    PrimaryKeyConstraint,
)
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.orm import relationship

from .base import Base, Session


class NaicsDescription(Base):
    """
    wrapper to category table
    """

    __tablename__ = "naics_descriptions"
    code = Column(psql.INTEGER, nullable=False, quote=False, name="code")
    description = Column(psql.TEXT, nullable=False, quote=False, name="description")
    __table_args__ = (PrimaryKeyConstraint("code", name="pk_naics_code"),)
    businesses = relationship("Business", back_populates="naics")

    def __init__(self, entry: Dict, **kwargs):
        self.code = entry["naics_number"]
        self.description = entry["industry"]

    def get_or_create(self, s: Session):
        row = s.query(NaicsDescription).filter_by(code=self.code).first()
        if row:
            return (row, False)
        s.add(self)
        s.flush()
        return (self, True)
