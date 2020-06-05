from pathlib import Path
import json
from typing import Dict

import requests

import config


class HereAuth:
    def __init__(self, MAIN_LOC: Path = Path(config.PROJECT_LOC)):
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
        self, loc_list, point, transportModeType: str = "car", searchRange: int = 20000
    ):
        params = self._set_params_distance(
            transportModeType=transportModeType, searchRange=searchRange
        )
        params.update(
            {
                f"start{i}": f"geo!{el['latitude']},{el['longitude']}"
                for i, el in enumerate(loc_list)
            }
        )
        params.update(
            {
                f"destination{i[0]}": f"geo!{point[0]},{point[1]}"
                for i in enumerate(loc_list)
            }
        )
        r = requests.get(url=self._route_url, params=params)
        return r
