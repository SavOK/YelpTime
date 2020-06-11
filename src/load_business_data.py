from pathlib import Path
import csv, json
import re
import io
from pprint import pprint
import itertools as itts

import boto3

from SQL import Session, Base, engine
from SQL import Business, NaicsDescription, Location


def conver_to_entry(row, naics_dict):
    def _to_int(R):
        try:
            I = int(float(R))
        except ValueError:
            I = None
        return I

    def _to_float(R):
        try:
            I = float(R)
        except ValueError:
            I = None
        return I

    def _convert_phone(num: str):
        str_n = num.replace("-", "")
        if len(str_n) == 10:
            return f"({str_n[:3]}) {str_n[3:6]} {str_n[6:]}"
        elif len(str_n) == 11:
            return f"({str_n[1:4]}) {str_n[4:7]} {str_n[7:]}"
        else:
            return

    def _get_emloyee_range(row):
        ptrn = re.compile(r"(?:[+-]|\()?\d+(?:,\d+)*(?:\.\d+)?\)?",)
        if len(row["TOTAL_EMPLOYEES"]) != 0:
            total = _to_int(row["TOTAL_EMPLOYEES"])
        elif len(row["EMPLOYEE_RANGE"]) != 0:
            m = ptrn.findall(row["EMPLOYEE_RANGE"])
            if len(m) == 2:
                total = _to_int(m[0].replace(",", ""))
            else:
                total = None
        else:
            total = None
        if total is None or total == 0:
            return
        if total <= 10:
            str_out = f"0 - 10"
        elif total <= 100:
            str_out = f"10 - 100"
        elif total <= 500:
            str_out = f"100 - 500"
        elif total <= 1000:
            str_out = f"500 - 1000"
        elif total <= 10000:
            str_out = f"1000 - 10000"
        elif total <= 100000:
            str_out = f"10000 - 100000"
        elif total <= 1000000:
            str_out = f"100000 - 1000000"
        elif total > 1000000:
            str_out = f"1000000 +"
        else:
            str_out = None
        return str_out

    def _get_sales_range(row):
        ptrn = re.compile(r"(?:[+-]|\()?\d+(?:,\d+)*(?:\.\d+)?\)?",)
        if len(row["SALES_VOLUME"]) != 0:
            total = _to_float(row["SALES_VOLUME"].replace(",", ""))
        elif len(row["SALES_VOLUME_RANGE"]) != 0:
            m = ptrn.findall(row["SALES_VOLUME_RANGE"])
            if len(m) == 2:
                total = _to_float(m[0].replace(",", ""))
            else:
                total = None
        else:
            total = None
        if total is None or total == 0:
            return
        if total <= 1000:
            str_out = f"0 - 1000"
        elif total <= 100000:
            str_out = f"1000 - 100000"
        elif total <= 500000:
            str_out = f"100000 - 500000"
        elif total <= 1000000:
            str_out = f"500000 - 1000000"
        elif total <= 5000000:
            str_out = f"1000000 - 5000000"
        elif total <= 20000000:
            str_out = f"5000000 - 20000000"
        elif total <= 100000000:
            str_out = f"20000000 - 100000000"
        elif total <= 1000000000:
            str_out = f"100000000 - 1000000000"
        elif total > 1000000000:
            str_out = f"1000000000 +"
        else:
            str_out = None
        return str_out

    out_data = {}
    if len(row["COMPANY_NAME"]) != 0:
        out_data["company_name"] = row["COMPANY_NAME"]
    else:
        out_data["company_name"] = None
    if len(row["SIC_CODE"]) != 0:
        out_data["sic_code"] = _to_int(row["SIC_CODE"])
    else:
        out_data["sic_code"] = None
    if len(row["SIC_DESCRIPTION"]) != 0:
        out_data["sic_description"] = row["SIC_DESCRIPTION"]
    else:
        out_data["sic_description"] = None
    if len(row["ADDRESS"]) != 0:
        out_data["address"] = row["ADDRESS"]
    else:
        out_data["address"] = None
    if len(row["CITY"]) != 0:
        out_data["city"] = row["CITY"]
    else:
        out_data["city"] = None
    if len(row["STATE"]) != 0:
        out_data["state"] = row["STATE"]
    else:
        out_data["state"] = None
    if len(row["ZIP"]) != 0:
        out_data["zip_code"] = row["ZIP"]
    else:
        out_data["zip_code"] = None
    if len(row["COUNTY"]) != 0:
        out_data["county"] = row["COUNTY"]
    else:
        out_data["county"] = None
    if len(row["PHONE"]) != 0:
        out_data["phone"] = _convert_phone(row["PHONE"])
    else:
        out_data["phone"] = None
    if len(row["FAX_NUMBER"]) != 0:
        out_data["fax"] = _convert_phone(row["FAX_NUMBER"])
    else:
        out_data["fax"] = None
    if len(row["WEBSITE"]) != 0:
        out_data["website"] = row["WEBSITE"]
    else:
        out_data["website"] = None
    if len(row["LATITUDE"]) > 0:
        out_data["latitude"] = _to_float(row["LATITUDE"])
    else:
        out_data["latitude"] = None
    if len(row["LONGITUDE"]) != 0:
        out_data["longitude"] = _to_float(row["LONGITUDE"])
    else:
        out_data["longitude"] = None
    out_data["employee_range"] = _get_emloyee_range(row)
    out_data["sales_volume_range"] = _get_sales_range(row)
    if len(row["NAICS_NUMBER"]) > 0:
        out_data["naics_number"] = _to_int(row["NAICS_NUMBER"])
    else:
        out_data["naics_number"] = None
    if len(row["INDUSTRY"]) > 0:
        out_data["industry"] = row["INDUSTRY"].lower()
    else:
        out_data["industry"] = None

    if out_data["zip_code"] is None or out_data["company_name"] is None:
        out_data["alias"] = None
    else:
        out_data["alias"] = (
            out_data["company_name"].replace(" ", "_").lower()
            + "_"
            + out_data["zip_code"]
        )
    if out_data["naics_number"] is None and out_data["industry"] is None:
        return out_data
    if out_data["naics_number"] is None:
        if out_data["industry"] in naics_dict:
            out_data["naics_number"] = naics_dict[out_data["industry"]]
    return out_data


def set_mybucket(bucket_name):
    s3 = boto3.resource("s3")
    return s3.Bucket(bucket_name)


def read_file(obj):
    all_data = []
    data = obj.get()["Body"].read().decode("windows-1252")
    reader = csv.DictReader(io.StringIO(data))
    for line in itts.islice(reader, 0, None):
        all_data.append(conver_to_entry(line))
    return all_data


def _filter_entry(entry):
    must_entry = [
        "company_name",
        "alias",
        "city",
        "state",
        "zip_code",
        "latitude",
        "longitude",
        "naics_number",
        "industry",
    ]
    return all(entry[x] is not None for x in must_entry)


def read_file(obj, naics: dict = None):
    if naics is None:
        with open("/home/ubuntu/YelpTime/data/naics_dict.json") as oF:
            naics = json.load(oF)
    all_data = []
    data = obj.get()["Body"].read().decode("windows-1252")
    reader = csv.DictReader(io.StringIO(data))
    for line in itts.islice(reader, 0, None):
        a = conver_to_entry(line, naics)
        if _filter_entry(a):
            yield a


if __name__ == "__main__":

    bucket_name = "saveliy.de.project"
    input_dir = "All_US_STATES"
    MyBucket = set_mybucket(bucket_name)
    Base.metadata.create_all(engine)

    s = Session()
    for obj in itts.islice(MyBucket.objects.filter(Prefix=input_dir), 0, None):
        if obj.key.endswith("/"):
            continue
        print(obj)
        for entry in itts.islice(read_file(obj), 0, None):
            B = Business(entry)
            B, isBnew = B.get_or_create(s)
            L = Location(entry)
            L, isLnew = L.get_or_create(s)
            C = NaicsDescription(entry)
            C, isCnew = C.get_or_create(s)
            B.naics = C
            B.location = L
            s.commit()
        print("Done object", obj)
    s.close()
