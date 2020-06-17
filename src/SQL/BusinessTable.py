from typing import Dict


from sqlalchemy import Column, Sequence
from sqlalchemy import PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql as psql

from .base import Base, Session


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
    id = Column(
        psql.BIGINT,
        Sequence("business_id_seq", metadata=Base.metadata),
        nullable=False,
        quote=False,
        name="id",
    )
    business_alias = Column(
        psql.TEXT, nullable=False, quote=False, name="business_alias", index=True
    )
    business_name = Column(psql.TEXT, nullable=False, quote=False, name="business_name")
    address = Column(psql.TEXT, nullable=True, quote=False, name="address")
    city = Column(psql.TEXT, nullable=False, quote=False, name="city")
    state = Column(psql.TEXT, nullable=False, quote=False, name="state")
    zip_code = Column(psql.TEXT, nullable=False, quote=False, name="zip_code")
    county = Column(psql.TEXT, nullable=True, quote=False, name="county")
    phone = Column(psql.TEXT, nullable=True, quote=False, name="phone")
    fax = Column(psql.TEXT, nullable=True, quote=False, name="fax")
    website = Column(psql.TEXT, nullable=True, quote=False, name="website")
    employee_range = Column(
        psql.TEXT, nullable=True, quote=False, name="employee_range"
    )
    sales_volume_range = Column(
        psql.TEXT, nullable=True, quote=False, name="sales_volume_range"
    )

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_businesses"),)

    naics_code = Column(psql.INTEGER, ForeignKey("naics_descriptions.code"))
    naics = relationship("NaicsDescription", back_populates="businesses")
    location_id = Column(psql.BIGINT, ForeignKey("locations.id"))
    location = relationship("Location", back_populates="businesses")

    def __init__(self, entry: Dict, **kwargs):
        self.business_alias = entry["alias"]
        self.business_name = entry["company_name"]
        self.address = entry["address"]
        self.city = entry["city"]
        self.state = entry["state"]
        self.zip_code = entry["zip_code"]
        self.county = entry["county"]
        if "phone" in entry:
            self.phone = entry["phone"]
        else:
            self.phone = None
        if "fax" in entry:
            self.fax = entry["fax"]
        else:
            self.fax = None
        if "website" in entry:
            self.website = entry["website"]
        else:
            self.website = None
        if "employee_range" in entry:
            self.employee_range = entry["employee_range"]
        else:
            self.employee_range = None
        if "sales_volume_range" in entry:
            self.sales_volume_range = entry["sales_volume_range"]
        else:
            self.sales_volume_range = None

    def get_or_create(self, s: Session):
        row = s.query(Business).filter_by(business_alias=self.business_alias).first()
        if row:
            return (row, False)
        s.add(self)
        s.flush()
        return (self, True)
