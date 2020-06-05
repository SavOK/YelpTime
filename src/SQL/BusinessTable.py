from typing import Dict

from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql as psql

from .base import Base, Session
from .AssociationTables import map_businesses_categories


class WrongEntryException(Exception):
    """
    Exception if bussiness entry format not matching
    """

    def __init__(self, massage):
        self.massage = massage


class Business(Base):
    """
    wrapper to businesses table
    """

    __tablename__ = "businesses"
    id = Column(psql.TEXT, nullable=False, quote=False, name="id")
    business_alias = Column(
        psql.TEXT, nullable=False, quote=False, name="business_alias"
    )
    latitude = Column(psql.REAL, nullable=False, quote=False, name="latitude")
    longitude = Column(psql.REAL, nullable=False, quote=False, name="longitude")
    display_phone = Column(psql.TEXT, nullable=True, quote=False, name="display_phone")
    image_url = Column(psql.TEXT, nullable=True, quote=False, name="image_url")
    is_closed = Column(psql.BOOLEAN, nullable=True, quote=False, name="is_closed")
    address1 = Column(psql.TEXT, nullable=True, quote=False, name="address1")
    address2 = Column(psql.TEXT, nullable=True, quote=False, name="address2")
    address3 = Column(psql.TEXT, nullable=True, quote=False, name="address3")
    city = Column(psql.TEXT, nullable=False, quote=False, name="city")
    country = Column(psql.TEXT, nullable=False, quote=False, name="country")
    state = Column(psql.TEXT, nullable=False, quote=False, name="state")
    zip_code = Column(psql.TEXT, nullable=False, quote=False, name="zip_code")
    display_address = Column(
        psql.TEXT, nullable=False, quote=False, name="display_address"
    )
    name = Column(psql.TEXT, nullable=False, quote=False, name="name")
    price = Column(psql.TEXT, nullable=True, quote=False, name="price")
    # rating = Column(psql.TEXT, nullable=True, quote=False, name="rating")
    review_counts = Column(
        psql.INTEGER, nullable=False, quote=False, name="review_counts", default=0
    )
    url = Column(psql.TEXT, nullable=False, quote=False, name="url")

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_businesses"),)

    categories = relationship(
        "Category", secondary=map_businesses_categories, backref="businesses"
    )
    location_id = Column(psql.BIGINT, ForeignKey("locations.id"))
    location = relationship("Location", back_populates="businesses")

    def __init__(self, entry: Dict, **kwargs):
        self.id = entry["id"]
        self.business_alias = entry["alias"]
        self.latitude = float(entry["coordinates"]["latitude"])
        self.longitude = float(entry["coordinates"]["longitude"])
        self.display_phone = entry["display_phone"]
        self.image_url = entry["image_url"]
        self.is_closed = entry["is_closed"]
        if entry["location"]["address1"] is None:
            self.address1 = None
        elif len(entry["location"]["address1"]) == 0:
            self.address1 = None
        else:
            self.address1 = entry["location"]["address1"]
        if entry["location"]["address2"] is None:
            self.address2 = None
        elif len(entry["location"]["address2"]) == 0:
            self.address2 = None
        else:
            self.address2 = entry["location"]["address2"]
        if entry["location"]["address3"] is None:
            self.address3 = None
        elif len(entry["location"]["address3"]) == 0:
            self.address3 = None
        else:
            self.address3 = entry["location"]["address3"]
        self.city = entry["location"]["city"]
        self.country = entry["location"]["country"]
        self.state = entry["location"]["state"]
        self.zip_code = entry["location"]["zip_code"]
        self.display_address = ", ".join(entry["location"]["display_address"])
        self.name = entry["name"]
        self.phone = entry["phone"]
        self.rating = entry["rating"]
        if "price" in entry:
            self.price = entry["price"]
        self.review_counts = entry["review_count"]
        self.url = entry["url"]

    def get_or_create(self, s: Session):
        row = s.query(Business).filter_by(id=self.id).first()
        if row:
            return (row, False)
        s.add(self)
        s.flush()
        return (self, True)
