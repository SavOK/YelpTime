from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as psql
from geoalchemy2 import Geometry, functions
from geoalchemy2.elements import WKTElement

from .base import Base, Session


class MainTable(Base):
    __tablename__ = "main_table"
    name = Column(psql.TEXT, nullable=False, quote=False, name="name", primary_key=True)
    name_alias = Column(psql.TEXT, nullable=False, quote=False, name="name_alias")
    address = Column(psql.TEXT, nullable=False, quote=True, name="address")
    city = Column(psql.TEXT, nullable=False, quote=False, name="city")
    state = Column(psql.TEXT, nullable=False, quote=False, name="state")
    zip_code = Column(psql.TEXT, nullable=False, quote=False, name="zip_code")
    county = Column(psql.TEXT, nullable=True, quote=False, name="county")
    phone = Column(psql.TEXT, nullable=True, quote=False, name="phone")
    fax = Column(psql.TEXT, nullable=True, quote=False, name="fax")
    latitude = Column(psql.REAL, nullable=True, quote=False, name="latitude")
    longitude = Column(psql.REAL, nullable=True, quote=False, name="longitude")
    employee_number = Column(
        psql.TEXT, nullable=True, quote=False, name="employee_number"
    )
    sales_volume = Column(psql.TEXT, nullable=True, quote=False, name="sales_volume")
    naics_code = Column(psql.TEXT, nullable=False, quote=False, name="naics_code")
    industry = Column(psql.TEXT, nullable=False, quote=False, name="industry")
    location = Column(Geometry("Point"), nullable=False, quote=False, name="location")
    location_4326 = Column(
        Geometry("Point"), nullable=False, quote=False, name="locattion_4326"
    )
