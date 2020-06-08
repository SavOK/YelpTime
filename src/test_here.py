from pathlib import Path
from typing import List, Tuple
import json
from operator import itemgetter
import sys

import requests
from sqlalchemy import alias
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Within
import pandas as pd

import config

from APIs import HereAuth, HereAPI
from SQL import Session
from SQL import Business, Location, Category


def get_isoline_generator(r: requests.models.Response) -> str:
    if r.status_code != 200:
        print("Something wrong with request")
        l = json.dumps(r.json(), indent=1)
        print(l)
        return
    data = r.json()
    isoline = data["response"]["isoline"][0]["component"][0]["shape"]
    for el in isoline:
        yield el.replace(",", "")


def query_points_within(isoline: str, s: Session):
    poligon = "POLYGON(({}))".format(isoline)
    q = (
        s.query(Business)
        .join(Location, Business.location_id == Location.id)
        .join(Category, Business.categories)
        .filter(Category.category_alias == "pizza")
        .filter(ST_Within(Location.location, poligon))
        .filter(Business.price != None)
    )
    return q


def generate_dict_from_query(q):
    for business in q.all():
        business_dict = {
            "name": business.name,
            "address": business.display_address,
            "price": business.price,
            "rating": business.rating,
            "latitude": business.latitude,
            "longitude": business.longitude,
            "reviews": business.review_counts,
        }
        yield business_dict


def get_data(point):
    HA = HereAPI()
    s = Session()
    r = HA.get_isoline(point[0], point[1])
    isoline = ",".join(get_isoline_generator(r))
    q = query_points_within(isoline, s)
    # return q
    # Q = get_data((40.8014, -73.9501))
    loc_list = list(generate_dict_from_query(q))

    r_m = HA.get_route_matrix(loc_list, point)

    dist_mat = r_m.json()
    # if 'response' not in dist_mat:
    #     return None
    mat_list = sorted(
        [x for x in dist_mat["response"]["matrixEntry"] if x["destinationIndex"] == 0],
        key=itemgetter("startIndex"),
    )
    for mat, loc in zip(mat_list, loc_list):
        loc.update(
            {
                "travelTime": mat["summary"]["travelTime"],
                "routeDistance": mat["summary"]["distance"],
            }
        )

    df = pd.DataFrame(loc_list)
    # print(
    #     df.sort_values(by=["travelTime", "routeDistance"]).reset_index(drop=True)[:10]
    # )
    return df


# if __name__ == "__main__":
#     # point = (42.306, -71.067)
#     point = (sys.argv[1], sys.argv[2])
#     print(point)
