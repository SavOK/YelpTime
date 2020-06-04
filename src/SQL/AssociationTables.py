from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects import postgresql as psql

from . import Base

map_businesses_categories = Table(
    "map_businesses_categories",
    Base.metadata,
    Column("business_id", psql.TEXT, ForeignKey("businesses.id")),
    Column("category_alias", psql.TEXT, ForeignKey("categories.category_alias")),
)
