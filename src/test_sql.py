from pathlib import Path
import json
from typing import Dict

from geoalchemy2 import Geometry
import geoalchemy2.functions as GeoFun

from SQL import Base, Session, engine
from SQL import Business, Category, Location

from APIs import YelpAPI

# r = Y.get_request(test_point[0], test_point[1])


def get_all_business_around_point(
    latitude: float, longitude: float, Y: YelpAPI = None
) -> Dict:
    if Y is None:
        Y = YelpAPI()
    # first run
    r = Y.get_request(latitude, longitude)
    if r.status_code != 200:
        print(
            f"at point {latitude} {longitude} offset 1 requests broke code {r.status_code}"
        )
        raise
    data = r.json()
    total = data["total"]
    read = len(data["businesses"])
    # next runs
    while read < total:
        print(f"{read}, {total}")
        r = Y.get_request(latitude, longitude, offset=read)
        if r.status_code != 200:
            print(
                f"at point {latitude} {longitude} requests broke code {r.status_code}"
            )
            raise
        curr_data = r.json()
        data["businesses"] += curr_data["businesses"]
        read = len(data["businesses"])
        if read >= 950:
            r = Y.get_request(latitude, longitude, offset=read, limit=1000 - read - 1)
            if r.status_code != 200:
                print(
                    f"at point {latitude} {longitude} requests broke code {r.status_code}"
                )
                raise
            curr_data = r.json()
            data["businesses"] += curr_data["businesses"]
            break
    return data


test_point = (42.3, -70.9060606060606)
in_data = get_all_business_around_point(*test_point)

# with open("/home/ubuntu/YelpTime/test.json", "w") as oF:
#     json.dump(in_data, oF, indent=2)

with open("/home/ubuntu/YelpTime/test.json") as oF:
    in_data = json.load(oF)

Base.metadata.create_all(engine)

s = Session()
# t1 = in_data["businesses"][4]
# P1 = Location(
#     location="POINT({} {})".format(
#         t1["coordinates"]["latitude"], t1["coordinates"]["longitude"]
#     )
# )
# t2 = in_data["businesses"][5]
# P2 = Location(
#     location="POINT({} {})".format(
#         t2["coordinates"]["latitude"], t2["coordinates"]["longitude"]
#     )
# )
# P3 = Location(location="POINT({} {})".format(test_point[0], test_point[1]))
for D in in_data["businesses"]:
    buisness = Business(D)
    buisness, isNewBus = buisness.get_or_create(s)
    for A in D["categories"]:
        category = Category(entry=A)
        category, isNewCat = category.get_or_create(s)
        buisness.categories.append(category)
    location = Location(D["coordinates"]["latitude"], D["coordinates"]["longitude"])
    location, isNewLoc = location.get_or_create(s)
    buisness.location = location
    s.commit()


# def object_as_dict(obj):
#     return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


# q = s.query(Location.id).filter(
#     GeoFun.ST_Equals(
#         Location.location, "POINT({} {})".format(test_point[0], test_point[1]),
#     )
# )
# # q = q.join(Business).limit(10)
# for r in q:
#     print(r)

# c = s.connection()
# stmt = text(
#     "SELECT bis.*, loc.* FROM businesses AS bis "
#     " JOIN locations AS loc "
#     " ON loc.id = bis.location_id"
#     " ORDER BY loc.location <#> ST_GeomFromEWKT('POINT(42.4030303030303 -71.05151515151516)') LIMIT 10"
# )
# r = c.execute(stmt)

s.close()
