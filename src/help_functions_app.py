"""
Help function for the app
Get list of states, 
Get DataFrame of the businesses around point 
"""
import json, csv
from pathlib import Path
import itertools as itts
from operator import itemgetter
from typing import List, Dict, Tuple

import requests
import pandas as pd

from sqlalchemy import distinct
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Within

import config

from APIs import HereAuth, HereAPI
from SQL import Session
from SQL import MainTable


def get_categories_list(InFile: Path = None) -> List[Dict]:
    """ Get list of business categories 
    Returns:
        List[Dict]: list of categories
    """

    def _get_category_dict(InFile: Path = InFile):
        if InFile is None:
            InFile = Path(config.DATA_LOC) / "6-digit_2017_Codes.csv"
        category_dict = {}
        with open(InFile, newline="", encoding="utf-8-sig") as oF:
            reader = csv.reader(oF)
            header = next(reader)
            for line in reader:
                category_dict[int(line[0])] = line[1].strip()
        return category_dict

    category_dict = _get_category_dict()
    category_list = [{"label": V, "value": K} for K, V in category_dict.items()]
    return category_list


def get_isoline(centerPoint: Tuple, rangePar: int, transportMode: str) -> str:
    """
    Get isoline string polygram around point with range limit
    Args:
        centerPoint (Tuple): Center point 
        rangePar (int): Range limit 
        transportMode (str): Transportation mode
    Returns:
        str: Isoline String for sql query
    """
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
    out_str = ",".join(el.replace(",", " ") for el in isoline)
    return out_str


def read_query(q):
    """
    Convert query results to dictionary
    Args:
        q [sqlalchemy.engine.result.ResultProxy]: SQL query resuts
    """

    def _convert_to_dict(row: Tuple) -> Dict:
        return {
            "name": row[0],
            "address_display": f"{row[1]}, {row[2]} {row[3]}, {row[4]}",
            "latitude": row[5],
            "longitude": row[6],
        }

    for el in itts.islice(q, 0, None):
        yield _convert_to_dict(el)


def get_data_around_point(
    centerPoint: Tuple, rangePar: int, transportMode: str, busnessType: str
) -> pd.DataFrame:
    """
    Get DataFrame of the points around point within limit
    """
    isoline = get_isoline(centerPoint, rangePar, transportMode)
    s = Session()
    c = s.connection()
    stm = """
    WITH SUBT AS (
        SELECT *, ST_MakePoint(B.latitude, B.longitude) as Point 
            FROM main_table AS B
            WHERE B.naics_code='{0}'
    )
    SELECT B.name, B.address, B.city, B.state, B.zip_code, B.latitude, B.longitude
        FROM SUBT AS B 
        WHERE ST_Within(B.Point, 'POLYGON(({1}))')
        ORDER BY
            B.Point <-> 'POINT({2} {3})'
        LIMIT 100;
    """.format(
        busnessType, isoline, centerPoint[0], centerPoint[1]
    )
    r = c.execute(stm)
    data = list(read_query(r))
    s.close()

    if len(data) == 0:
        print(f"Nothing found around {centerPoint}")
        return

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


# df = get_data_around_point([33.50919623713959, -86.84928244609489], 60, "car", 722511)
def get_state_coord_dict():
    return {
        "AK": (61.167624, -149.870273),
        "AL": (33.507653, -86.809375),
        "AR": (34.738450, -92.281194),
        "AZ": (33.479755, -112.080412),
        "CA": (37.713170, -121.925008),
        "CO": (39.716258, -105.009264),
        "CT": (41.748521, -72.679510),
        "DC": (38.897345, -77.044744),
        "DE": (39.713688, -75.542797),
        "FL": (28.526044, -81.427583),
        "GA": (32.840029, -83.656105),
        "HI": (21.316393, -157.853710),
        "IA": (41.582120, -93.574039),
        "ID": (43.564172, -116.135502),
        "IL": (40.503895, -88.987183),
        "IN": (39.739573, -86.181439),
        "KS": (38.824448, -97.624704),
        "KY": (38.009101, -84.575379),
        "LA": (30.272183, -92.053513),
        "MA": (42.339085, -71.173171),
        "MD": (39.269676, -76.636874),
        "ME": (44.754408, -68.766797),
        "MI": (42.749894, -83.497057),
        "MN": (44.953774, -93.373187),
        "MO": (38.924986, -92.300594),
        "MS": (32.371442, -90.136782),
        "MT": (45.760004, -111.165712),
        "NC": (35.305659, -80.789104),
        "ND": (46.800341, -100.731545),
        "NE": (40.842962, -96.763035),
        "NH": (43.044909, -71.457311),
        "NJ": (40.177446, -74.689891),
        "NM": (35.155775, -106.555892),
        "NV": (36.245775, -115.198838),
        "NY": (42.641542, -73.761615),
        "OH": (40.008934, -82.934764),
        "OK": (35.343917, -97.418445),
        "OR": (44.915568, -122.977644),
        "PA": (40.371835, -76.978961),
    }


def get_list_of_states() -> List[Dict]:
    """Get list of states for 
    Returns:
       List[Dict]: List of States for dropdown 
    """
    state_dict = get_state_coord_dict()
    state_list = [{"value": x, "label": x} for x in state_dict.keys()]
    return sorted(state_list, key=itemgetter("value"))
