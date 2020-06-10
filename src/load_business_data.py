from pathlib import Path
import csv
from pprint import pprint
import itertools as itts


from SQL import Session
from SQL import Business, SicDescription, Location


def conver_to_entry(row):
    out_data = {}
    if "COMPANY_NAME" in row:
        out_data["company_name"] = row["COMPANY_NAME"]
    else:
        out_data["company_name"] = None

    # 'company_name':, row['COMPANY_NAME'],
    # 'sic_code':
    # }

    pass


test_file = Path("/home/ubuntu/business_data_367.csv")
with open(test_file, newline="") as oF:
    reader = csv.DictReader(oF)
    for row in itts.islice(reader, 0, 10):
        pprint(row)
