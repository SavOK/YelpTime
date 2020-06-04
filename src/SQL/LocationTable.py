from typing import Dict, Tuple
from sqlalchemy import (
    Column,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy import Sequence
from sqlalchemy.dialects import postgresql as psql
from geoalchemy2 import Geometry, functions
from geoalchemy2.elements import WKTElement

from .base import Base, Session

# from .BusinessTable import Business


class Location(Base):
    __tablename__ = "locations"
    id = Column(
        psql.BIGINT,
        Sequence("point_id_seq", metadata=Base.metadata),
        nullable=False,
        name="id",
        quote=False,
    )
    location = Column(Geometry("Point"), nullable=False, quote=False, name="location")
    __table_args__ = (PrimaryKeyConstraint("id", name="pk_location_id"),)
    businesses = relationship("Business", back_populates="location")

    def __init__(self, latitude: float, longitude: float):
        self.location = WKTElement("POINT({} {})".format(latitude, longitude))

    def get_or_create(self, s: Session) -> Tuple:
        row = s.query(Location).filter(
            functions.ST_Equals(Location.location, self.location,)
        ).first()
        if row:
            return (row, False)
        s.add(self)
        s.flush()
        return (self, True)
