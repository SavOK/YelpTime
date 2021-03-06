"""
Class interacts with Here.API
"""

from pathlib import Path
import json
from typing import Dict, List, Tuple

import requests

import config


class HereAuth:
    def __init__(self, MAIN_LOC: Path = Path(config.PROJECT_LOC)):
        """
        Generate key and id to interact with HERE API
        Args:
            MAIN_LOC (Path, optional): Location of the file with keys. Defaults to Path(config.PROJECT_LOC). 
        """
        self._main_loc = MAIN_LOC
        self._data = self._keys_data()

    def _keys_data(self, MAIN_LOC: Path = None) -> Dict:
        if MAIN_LOC is None:
            MAIN_LOC = self._main_loc
        file_loc = MAIN_LOC / ".configs"
        file_path = file_loc / "here.api"
        if not file_path.is_file():
            raise FileNotFoundError("API KEY file: {} not there".format(file_path))
        with open(file_path) as oF:
            return json.load(oF)

    def get_key(self):
        return self._data["Key"]

    def get_id(self):
        return self._data["ID"]


class HereAPI:
    _isoline_url = (
        "https://isoline.route.ls.hereapi.com/routing/7.2/calculateisoline.json?"
    )
    _route_url = "https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json"

    def __init__(self, DATA_LOC=Path(config.DATA_LOC)):
        """
        Responce functions to interact with Here.API
        Args:
            DATA_LOC ([type], optional):  Defaults to Path(config.DATA_LOC).
        """
        self._data_loc = DATA_LOC

    def _set_params_isoline(
        self,
        latitude: float,
        longitude: float,
        rangePar: int,
        rangeType: str,
        transportModeType: str,
    ) -> Dict:
        HA = HereAuth()
        if transportModeType not in {"car", "pedestrian"}:
            raise TypeError("Allowed values car; pedestrian")
        if transportModeType == "car":
            mode = f"fastest;{transportModeType};traffic:enabled"
        else:
            mode = f"shortest;{transportModeType};"
        params = {
            "apiKey": HA.get_key(),
            "app_id": HA.get_id(),
            "start": "geo!{},{}".format(latitude, longitude),
            "range": rangePar,
            "rangeType": rangeType,
            "mode": mode,
            # "maxPoints": 50,
        }
        return params

    def get_isoline(
        self,
        latitude: float,
        longitude: float,
        rangePar: int = 300,
        rangeType: str = "time",
        transportModeType: str = "car",
    ) -> requests.models.Response:
        """ 
        Get isoline, peremitter around point reachable in specified time
        Args:
            latitude (float): latitude of the point
            longitude (float): longitude of the point
            rangePar (int, optional): time limit in seconds or distance in meters. Defaults to 300.
            rangeType (str, optional): range limit type time|distance. Defaults to "time".
            transportModeType (str, optional): transportation type car|pedestrian. Defaults to "car".
        Returns:
            requests.models.Response: return response 
        """
        params = self._set_params_isoline(
            latitude=latitude,
            longitude=longitude,
            rangePar=rangePar,
            rangeType=rangeType,
            transportModeType=transportModeType,
        )
        r = requests.get(url=self._isoline_url, params=params)
        return r

    def _set_params_distance(self, transportModeType: str, searchRange: int) -> Dict:
        HA = HereAuth()
        if transportModeType not in {"car", "pedestrian"}:
            raise TypeError("Allowed values car; pedestrian")
        if transportModeType == "car":
            mode = f"fastest;{transportModeType};traffic:enabled"
        else:
            mode = f"shortest;{transportModeType};"
        params = {
            "apiKey": HA.get_key(),
            "app_id": HA.get_id(),
            "mode": mode,
            "searchRange": searchRange,
            "summaryAttributes": "distance,traveltime",
            "searchRange": searchRange,
        }
        return params

    def get_route_matrix(
        self,
        loc_list: List,
        point: Tuple,
        transportModeType: str = "car",
        searchRange: int = 20000,
    ) -> requests.models.Response:
        """
        Get distance matrix request from point 
        Args:
            loc_list (List): List of the locations (len <= 100)
            point (Tuple): Center point
            transportModeType (str, optional): Mode of transportation. Defaults to "car".
            searchRange (int, optional): Search limit. Defaults to 20000.
        Returns:
            requests.models.Response: response 
        """
        params = self._set_params_distance(
            transportModeType=transportModeType, searchRange=searchRange
        )
        params.update(
            {
                f"destination{i}": f"geo!{el['latitude']},{el['longitude']}"
                for i, el in enumerate(loc_list[:100])
            }
        )
        params.update({"start0": f"geo!{point[0]},{point[1]}"})
        r = requests.get(url=self._route_url, params=params)
        return r
