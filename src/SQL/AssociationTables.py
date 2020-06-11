# from sqlalchemy import Column, ForeignKey, Table
# from sqlalchemy.dialects import postgresql as psql

# from . import Base

# map_businesses_sic_code = Table(
#     "map_businesses_sic_code",
#     Base.metadata,
#     Column("business_id", psql.TEXT, ForeignKey("businesses.id")),
#     Column("sic_code", psql.TEXT, ForeignKey("cis_descriptions.sic_code")),
# )
