"""

"""
from pathlib import Path
import json
from typing import Dict

import requests

import config


class YelpAuth:
    def __init__(self, MAIN_LOC: Path = Path(config.PROJECT_LOC)):
        self._main_loc = MAIN_LOC
        self._data = self._keys_data()

    def _keys_data(self, MAIN_LOC: Path = None) -> Dict:
        if MAIN_LOC is None:
            MAIN_LOC = self._main_loc
        file_loc = MAIN_LOC / ".configs"
        file_path = file_loc / "yelp.api"
        if not file_path.is_file():
            raise FileNotFoundError("API KEY file: {} not there".format(file_path))
        with open(file_path) as oF:
            return json.load(oF)

    def get_key(self):
        return self._data["Key"]

    def get_id(self):
        return self._data["ID"]


class YelpAPI:
    _search_url = "https://api.yelp.com/v3/businesses/search"

    def __init__(self, DATA_LOC=Path(config.DATA_LOC), radius: int = 250):
        self._data_loc = DATA_LOC
        self.default_radius = radius

    def _get_categories(self, DATA_LOC: Path = None) -> str:
        if DATA_LOC is None:
            DATA_LOC = self._data_loc
        category_file = DATA_LOC / "categories.json"
        if not category_file.is_file():
            raise FileNotFoundError(
                "Yelp category file: {} not there".format(category_file)
            )
        with open(category_file) as oF:
            data = json.load(oF)
        cat = (el["alias"] for el in data if len(el["parents"]) == 0)
        return ",".join(cat)

    def _set_params(
        self,
        latitude: float,
        longditude: float,
        radius: int = None,
        categories: str = None,
        limit: int = 50,
        offset: int = None,
    ) -> Dict:
        if radius is None:
            radius = self.default_radius
        if categories is None:
            categories = self._get_categories()
        out_dict = {
            "latitude": latitude,
            "longitude": longditude,
            "radius": radius,
            "categories": categories,
            "limit": limit,
        }
        if offset is not None:
            out_dict.update({"offset": offset})
        return out_dict

    def get_request(
        self,
        latitude: float,
        longditude: float,
        radius: int = None,
        categories: str = None,
        limit: int = 50,
        offset: int = None,
    ):
        YA = YelpAuth()
        header = {"Authorization": "bearer {}".format(YA.get_key())}
        params = self._set_params(
            latitude=latitude,
            longditude=longditude,
            radius=radius,
            categories=categories,
            limit=limit,
            offset=offset,
        )
        r = requests.get(url=self._search_url, params=params, headers=header)
        return r
