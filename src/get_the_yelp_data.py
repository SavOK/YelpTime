import json
import itertools as itts
from pathlib import Path
from typing import Dict

import numpy as np
from pathlib import Path
import json

from SQL import Base, Session, engine
from SQL import Business, Category, Location

from APIs import YelpAPI
from APIs import YelpAuth, YelpAPI


def generate_box():
    box_dim = (23000, 25000)  # dim of the box in meters
    step_size = 250  # in meters

    num_steps = tuple([int(x / step_size) for x in box_dim])
    box = {
        "SE": (42.3, -70.9),
        "NE": (42.5, -70.9),
        "SW": (42.3, -71.2),
        "NW": (42.5, -71.2),
        "grid_size": (100, 100),  # makes about 25k x 25k box with step 250
    }
    box["S_TO_N"] = np.linspace(box["SE"][0], box["NE"][0], box["grid_size"][0])
    box["E_TO_W"] = np.linspace(box["SE"][1], box["SW"][1], box["grid_size"][1])
    return box


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
        r = YelpAPI.get_request(latitude, longitude, offset=(read + 1))
        if r.status_code != 200:
            print(
                f"at point {latitude} {longitude} requests broke code {r.status_code}"
            )
            raise
        curr_data = r.json()
        data["businesses"] += curr_data["businesses"]
        read = len(data["business"])
    return data


def add_data_to_table(in_data: Dict):
    s = Session()
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
    s.close()


if __name__ == "__main__":
    Y = YelpAPI()
    Base.metadata.create_all(engine)
    box = generate_box()
    for ix, latitude in enumerate(box["S_TO_N"]):
        for iy, longitude in enumerate(box["E_TO_W"]):
            print(f"proccesing point {ix} {iy} {latitude} {longitude}")
            data = get_all_business_around_point(latitude, longitude, Y)
            add_data_to_table(data)
            print(
                f"Done proccesing point {ix} {iy} {data['total']} {len(data['businesses'])}"
            )
