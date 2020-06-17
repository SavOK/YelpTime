import json, csv
from pathlib import Path
import itertools as itts
from operator import itemgetter
from pprint import pprint
from typing import List, Dict

import requests
import pandas as pd

from sqlalchemy import distinct
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Within

import config

from APIs import HereAuth, HereAPI
from SQL import Session
from SQL import Business, Location, NaicsDescription


def get_categories_list(InFile: Path = None) -> List[Dict]:
    """ Get list of business categories 
    Returns:
        List[Dict]: list of categories
    """

    def get_category_dict(InFile: Path = InFile):
        if InFile is None:
            InFile = Path(config.DATA_LOC) / "6-digit_2017_Codes.csv"
        category_dict = {}
        with open(InFile, newline="", encoding="utf-8-sig") as oF:
            reader = csv.reader(oF)
            for line in reader:
                category_dict[int(line[0])] = line[1].strip()
        return category_dict

    category_dict = get_category_dict()
    category_list = [{"label": V, "value": K} for K, V in category_dict.items()]
    return category_list


def get_isoline(centerPoint, rangePar, transportMode) -> str:
    HA = HereAPI()
    r = HA.get_isoline(
        latitude=centerPoint[0],
        longitude=centerPoint[1],
        rangePar=rangePar,
        transportModeType=transportMode,
    )
    if r.status_code != 200:
        print("Something wrong with isoline request")
        l = json.dumps(r.json(), indent=1)
        pprint(l)
    data = r.json()
    isoline = data["response"]["isoline"][0]["component"][0]["shape"]
    out_str = ",".join(el.replace(",", "") for el in isoline)
    return out_str


def convert_to_dict(row):
    return {
        "name": row.business_name,
        "address_display": f"{row.address}, {row.city} {row.state}, {row.zip_code}",
        "street": row.address,
        "city": row.city,
        "state": row.state,
        "zip": row.zip_code,
        "latitude": row.location.latitude,
        "longitude": row.location.longitude,
    }


def read_query(q):
    if q.filter(q.exists()).first() is None:
        return None

    for el in itts.islice(q, 0, None):
        yield convert_to_dict(el)


def get_data_around_point(centerPoint, rangePar, transportMode, busnessType):
    isoline = get_isoline(centerPoint, rangePar, transportMode)
    poligon = f"POLYGON(({isoline}))"
    s = Session()
    q = (
        s.query(Business)
        .join(Location, Business.location_id == Location.id)
        .filter(Business.naics_code == busnessType)
        .filter(ST_Within(Location.location, poligon))
        .filter(Business.address != "None")
    )
    data = list(read_query(q))[:100]
    if len(data) == 0:
        print(f"Nothing found around {centerPoint}")
        return

    s.close()
    HA = HereAPI()
    if transportMode == "car":
        rangeSear = rangePar * 200
    else:
        rangeSear = rangePar * 10
    r = HA.get_route_matrix(
        loc_list=data,
        point=centerPoint,
        transportModeType=transportMode,
        searchRange=rangeSear,
    )
    if r.status_code != 200:
        print("Something wrong with matrix request")
        l = json.dumps(r.json(), indent=1)
        pprint(l)
    dist_data = r.json()
    dist_matrix = sorted(
        dist_data["response"]["matrixEntry"], key=itemgetter("destinationIndex")
    )
    if len(dist_matrix) == 0:
        pprint(r.json())
    if "summary" not in dist_matrix[0]:
        pprint(r.json())
    for ix, dist in enumerate(dist_matrix):
        data[ix].update(
            {
                "distance": dist["summary"]["distance"],
                "travel": dist["summary"]["travelTime"],
            }
        )
    return pd.DataFrame(data)


df = get_data_around_point([33.50919623713959, -86.84928244609489], 900, "car", 722511)


def get_list_of_states():
    s = Session()
    q = s.query(distinct(Business.state))
    state_list = [{"value": x[0], "label": x[0]} for x in q.all()]
    return state_list


def get_state_coord_dict():
    return {
        "AK": (61.167624, -149.870273),
        "AL": (33.507653, -86.809375),
        "AR": (34.738450, -92.281194),
        "AZ": (33.479755, -112.080412),
    }
