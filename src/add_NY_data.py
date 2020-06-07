from pathlib import Path
import itertools as itts
import csv
import random
import string

import config

from SQL import Session
from SQL import Business, Location, Category


def get_random_string(stringLength=24):
    lettersAndDigits = string.ascii_letters + string.digits
    return "".join((random.choice(lettersAndDigits) for i in range(stringLength)))


def get_phone(S: str) -> str:
    if len(S) == 10:
        return f"({S[:3]}) {S[3:6]}-{S[6:]}"
    elif len(S) == 11:
        s = S[1:]
        return f"({s[:3]}) {s[3:6]}-{s[6:]}"
    else:
        return ""


def get_address(R) -> dict:
    adr = f"{R['Address Building']} {R['Address Street Name']}"
    if len(R["Secondary Address Street Name"]) > 0:
        adr += f" {R['Secondary Address Street Name']}"
    adr += ","
    adr += f" {R['Address City'].capitalize()}, "
    adr += f"{R['Address State']} {R['Address ZIP']}"
    return adr


def get_all_data(InFile):
    all_data = {}
    alias_dict = {}
    with open(InFile, newline="") as oF:
        CSVReader = csv.DictReader(oF, delimiter=",", quotechar='"')
        for row in itts.islice(CSVReader, 0, None):
            if row["Location"] == "":
                continue
            if row["Latitude"] == "":
                continue
            if row["Longitude"] == "":
                continue
            ids = get_random_string(24) + "_ny_lic"
            while ids in all_data.keys():
                ids = get_random_string(24) + "_ny_lic"
            alias = row["Business Name"].lower().replace(" ", "_")
            if alias in alias_dict:
                alias_dict[alias] = alias_dict[alias] + 1
            else:
                alias_dict[alias] = 1
            all_data[ids] = {
                "id": ids,
                "alias": f"{alias}_{alias_dict[alias]}",
                "latitude": round(float(row["Latitude"]), 4),
                "longitude": round(float(row["Longitude"]), 4),
                "coordinates": {
                    "latitude": round(float(row["Latitude"]), 4),
                    "longitude": round(float(row["Longitude"]), 4),
                },
                "display_phone": get_phone(row["Contact Phone Number"]),
                "image_url": None,
                "is_closed": False,
                "location": {
                    "address1": f"{row['Address Building']} {row['Address Street Name']}",
                    "address2": f"{row['Secondary Address Street Name']}",
                    "address3": "",
                    "city": f"{row['Address City']}",
                    "country": "US",
                    "state": f"{row['Address State']}",
                    "zip_code": f"{row['Address ZIP']}",
                    "display_address": [get_address(row)],
                },
                "name": row["Business Name"],
                "price": None,
                "rating": None,
                "review_counts": 0,
                "url": None,
                "source_db": "NY_License",
                "categories": [
                    {
                        "alias": row["Industry"].lower().replace(" ", ""),
                        "title": row["Industry"],
                    }
                ],
            }
    return all_data


if __name__ == "__main__":
    data_file = Path(config.DATA_LOC) / "Legally_Operating_Businesses.csv"
    all_data = get_all_data(data_file)
    s = Session()
    for B in all_data.values():
        B["is_closed"] = False
        business = Business(B)
        business.source_db = "NY_License"
        business, isNewBus = business.get_or_create(s)
        for A in B["categories"]:
            category = Category(entry=A)
            category, isNewCat = category.get_or_create(s)
            business.categories.append(category)
        location = Location(B["latitude"], B["longitude"])
        location, isNewLoc = location.get_or_create(s)
        business.location = location
        s.commit()
    s.close()
