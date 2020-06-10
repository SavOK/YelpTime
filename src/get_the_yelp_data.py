import json
import sys
import itertools as itts

from pathlib import Path
from pprint import pprint
import time
from typing import Dict, List

import numpy as np

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


def test_request(r, warning_msq) -> bool:
    if r.status_code != 200:
        err_msg = json.dumps(r.json(), indent=1)
        pprint(f"WARNING {warning_msq}", sys.stderr)
        pprint(f"ERROR STATUS CODE {r.status_code}", sys.stderr)
        pprint(err_msg, sys.stderr)
        return False
    D = r.json()
    if "businesses" not in D:
        pprint(f"WARNING {warning_msq}", sys.stderr)
        pprint(f"ERROR STATUS CODE {r.status_code}", sys.stderr)
        pprint(f"businesses not in data", sys.stderr)
        return False
    if "total" not in D:
        pprint(f"WARNING {warning_msq}", sys.stderr)
        pprint(f"ERROR STATUS CODE {r.status_code}", sys.stderr)
        pprint(f"total not in data", sys.stderr)
        return False
    return True


def get_requests_around_point_for_sub_category(
    latitude, longitude, Y: YelpAPI, category: List
):
    time.sleep(1)
    r = Y.get_request(latitude, longitude, categories=",".join(category))
    if not test_request(r, f" loc ({latitude} {longitude})"):
        return
    D = r.json()
    read = len(D["businesses"])
    total = D["total"]
    while read < total:
        time.sleep(1)
        if (1000 - read) >= 50:
            r = Y.get_request(
                latitude, longitude, categories=",".join(category), offset=read
            )
            if not test_request(
                r, f" loc ({latitude} {longitude}) offset {read}\n{','.join(category)}"
            ):
                return D
        else:
            r = Y.get_request(
                latitude,
                longitude,
                categories=",".join(category),
                offset=read,
                limit=(1000 - read),
            )
            if not test_request(
                r,
                f" loc ({latitude} {longitude}) offset {read} limit {1000-read}\n{','.join(category)}",
            ):
                return D
        curr_data = r.json()
        D["businesses"] += curr_data["businesses"]
        read = len(D["businesses"])
    return D


def get_all_business_around_point(
    latitude: float, longitude: float, Y: YelpAPI = None
) -> Dict:
    if Y is None:
        Y = YelpAPI()
    # first run
    time.sleep(1)
    r = Y.get_request(latitude, longitude)
    if not test_request(r, f" loc ({latitude} {longitude})"):
        if r.status_code == 429:
            sys.exit()
        return

    data = r.json()
    total = data["total"]
    read = len(data["businesses"])
    all_categories = Y.list_of_categories()
    if read == total:
        return data
    elif total >= 1000:
        if total > 1500:
            categories_chunks = [
                all_categories[i : i + 1] for i in range(0, len(all_categories), 1)
            ]
        else:
            categories_chunks = [
                all_categories[i : i + 4] for i in range(0, len(all_categories), 4)
            ]
        for categ in categories_chunks:
            curr_data = get_requests_around_point_for_sub_category(
                latitude, longitude, Y, categ
            )
            if curr_data is None:
                continue
            data["businesses"] += curr_data["businesses"]
    else:
        curr_data = get_requests_around_point_for_sub_category(
            latitude, longitude, Y, all_categories
        )
        if curr_data is None:
            return data
        data["businesses"] += curr_data["businesses"]
    return data


def add_data_to_table(in_data: Dict):
    s = Session()
    for D in in_data["businesses"]:
        if D["coordinates"]["latitude"] is None:
            continue
        business = Business(D)
        business.source_db = "Yelp_API"
        business, isNewBus = business.get_or_create(s)
        for A in D["categories"]:
            category = Category(entry=A)
            category, isNewCat = category.get_or_create(s)
            business.categories.append(category)
        location = Location(D["coordinates"]["latitude"], D["coordinates"]["longitude"])
        location, isNewLoc = location.get_or_create(s)
        business.location = location
        s.commit()
    s.close()


if __name__ == "__main__":
    Y = YelpAPI()
    Base.metadata.create_all(engine)

    box = generate_box()
    # test_point = (42.348484848484844, -71.15151515151516)
    for ix, latitude in enumerate(box["S_TO_N"][90:91], start=90):
        for iy, longitude in enumerate(box["E_TO_W"][68:], start=68):
            print(f"proccesing point {ix} {iy} {latitude} {longitude}")
            data = get_all_business_around_point(latitude, longitude, Y)
            if data is None:
                continue
            if data["total"] == 0:
                time.sleep(1)
                print("Done 0 out of 0")
                continue
            add_data_to_table(data)
            print(
                f"Done {len(set(x['id'] for x in data['businesses']))} out of {data['total']}"
            )
