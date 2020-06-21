from pathlib import Path
import itertools as itts
import os
import time
import json
import csv
import re
from typing import List, Dict

from pyspark.sql import SparkSession, Row, SQLContext
from pyspark.context import SparkContext
import pyspark.sql.functions as F
from pyspark.sql.types import StructField, StructType
from pyspark.sql.types import StringType, IntegerType, FloatType

import config


def read_category_dict() -> Dict:
    out_dict = {}
    with open(
        Path(config.DATA_LOC) / "6-digit_2017_Codes.csv",
        encoding="utf-8-sig",
        newline="",
    ) as oF:
        reader = csv.reader(oF)
        header = [x.strip() for x in next(reader)[:2]]
        for line in reader:
            curr_line = [x.strip() for x in line[:2]]
            out_dict[curr_line[0]] = {k: v for k, v in zip(header, curr_line)}
            out_dict[curr_line[0]]["alias"] = curr_line[1].lower().replace(" ", "_")
    return out_dict


def clean_line(row, naics_dict):
    def _to_int(S):
        try:
            I = int(float(S))
        except ValueError:
            I = None
        return I

    def _to_float(S):
        try:
            I = float(S)
        except ValueError:
            I = None
        return I

    def _convert_phone(num: str):
        num = num.replace("-", "")
        if len(num) == 10:
            return f"({num[:3]}) {num[3:6]} {num[6:]}"
        elif len(num) == 11:
            return f"({num[1:4]}) {num[4:7]} {num[7:]}"
        else:
            return

    def _get_emloyee_value(D):
        ptrn = re.compile(r"(?:[+-]|\()?\d+(?:,\d+)*(?:\.\d+)?\)?",)
        if D["TOTAL_EMPLOYEES"] is not None:
            total = _to_int(D["TOTAL_EMPLOYEES"])
        elif D["EMPLOYEE_RANGE"] is not None:
            m = ptrn.findall(D["EMPLOYEE_RANGE"])
            if len(m) == 2:
                total = _to_int(m[0].replace(",", ""))
            else:
                total = None
        else:
            return
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

    def _get_sales_value(D):
        ptrn = re.compile(r"(?:[+-]|\()?\d+(?:,\d+)*(?:\.\d+)?\)?",)
        if D["SALES_VOLUME"] is not None:
            total = _to_float(D["SALES_VOLUME"].replace(",", ""))
        elif D["SALES_VOLUME_RANGE"] is not None:
            m = ptrn.findall(D["SALES_VOLUME_RANGE"])
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

    row_dict = row.asDict()
    out_dict = {}
    name_str = row_dict["COMPANY_NAME"].lower().replace('"', "").strip()
    out_dict["name"] = " ".join(x.capitalize() for x in name_str.split())
    out_dict["name_alias"] = name_str.replace(" ", "_")

    if row_dict["ADDRESS"] is not None:
        out_dict["address"] = row_dict["ADDRESS"].replace('"', "").strip()
    else:
        out_dict["address"] = None
    out_dict["city"] = " ".join(
        x.capitalize().strip() for x in row_dict["CITY"].replace('"', "").split()
    )
    out_dict["state"] = row_dict["STATE"].replace('"', "").strip()
    out_dict["zip_code"] = row_dict["ZIP"].replace('"', "").strip()
    if row_dict["COUNTY"] is not None:
        out_dict["county"] = " ".join(
            x.strip().capitalize() for x in row_dict["COUNTY"].replace('"', "").split()
        )
    else:
        out_dict["county"] = None
    if row_dict["PHONE"] is not None:
        out_dict["phone"] = _convert_phone(row_dict["PHONE"])
    else:
        out_dict["phone"] = None
    if row_dict["FAX_NUMBER"] is not None:
        out_dict["fax"] = _convert_phone(row_dict["FAX_NUMBER"])
    else:
        out_dict["fax"] = None

    out_dict["latitude"] = _to_float(row_dict["LATITUDE"].replace('"', ""))
    out_dict["longitude"] = _to_float(row_dict["LONGITUDE"].replace('"', ""))
    if (out_dict["longitude"] is not None) and (out_dict["longitude"] > 0):
        out_dict["longitude"] = out_dict["longitude"] * (-1)
    out_dict["employee_number"] = _get_emloyee_value(row_dict)
    out_dict["sales_volume"] = _get_sales_value(row_dict)
    out_dict["naics_code"] = row_dict["NAICS_NUMBER"].strip()
    if out_dict["naics_code"] in naics_dict:
        out_dict["industry"] = naics_dict[out_dict["naics_code"]]["title"]
    else:
        out_dict["industry"] = None
    return Row(**out_dict)


def _set_schema():
    fields = [
        StructField("name", StringType(), False),
        StructField("name_alias", StringType(), False),
        StructField("address", StringType(), True),
        StructField("city", StringType(), False),
        StructField("state", StringType(), False),
        StructField("zip_code", StringType(), False),
        StructField("county", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("fax", StringType(), True),
        StructField("latitude", FloatType(), True),
        StructField("longitude", FloatType(), True),
        StructField("employee_number", StringType(), True),
        StructField("sales_volume", StringType(), True),
        StructField("naics_code", StringType(), False),
        StructField("industry", StringType(), True),
    ]
    return StructType(fields)


if __name__ == "__main__":

    category_dict = read_category_dict()
    columns_drop = [
        "CONTACT_FIRSTNAME",
        "CONTACT_LASTNAME",
        "CONTACT_FULLNAME",
        "CONTACT_GENDER",
        "CONTACT_TITLE",
        "CONTACT2_FIRSTNAME",
        "CONTACT2_LASTNAME",
        "CONTACT2_TITLE",
        "CONTACT2_GENDER",
        "SIC_CODE",
        "SIC_DESCRIPTION",
        "INDUSTRY",
        "WEBSITE",
    ]
    # create session

    ss = (
        SparkSession.builder.appName("ReadAllData")
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID"))
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY"))
        .config("spark.executor.memory", "6G")  # memory per executer
        .config(
            "spark.driver.extraClassPath", os.getenv("HOME") + "/postgresql-42.2.14.jar"
        )
        .config(
            "spark.jars.packages",
            "com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.7",
        )
        .getOrCreate()
    )
    sqlContext = SQLContext(ss)
    dataframe = ss.read.csv(
        "s3a://saveliy.de.project/All_US_STATES/*.csv",
        encoding="windows-1252",
        header=True,
    )
    # step 0 remove extra columns
    df = dataframe.repartition("STATE").drop(*columns_drop)
    # step 1 filter locations, company name, naics code
    df = (
        df.filter(F.col("LATITUDE").isNotNull() & F.col("LONGITUDE").isNotNull())
        .filter(
            F.col("ZIP").isNotNull()
            & F.col("STATE").isNotNull()
            & F.col("STATE").isNotNull()
        )
        .filter(F.col("COMPANY_NAME").isNotNull())
        .filter(F.col("NAICS_NUMBER").isNotNull())
    )
    # step 2 clean data
    schema = _set_schema()
    rdd = df.rdd.map(lambda r: clean_line(r, naics_dict=category_dict))
    clean_df = (
        sqlContext.createDataFrame(data=rdd, schema=schema)
        .filter(F.col("industry").isNotNull())
        .filter(F.col("latitude").isNotNull() & F.col("longitude").isNotNull())
    )
    num_lines = clean_df.count()

    # saving to postgres
    save_df = (
        clean_df.write.format("jdbc")
        .option("url", "jdbc:postgresql://54.226.115.222:5432/business")
        .option("driver", "org.postgresql.Driver")
        .option("dbtable", "public.main_table")
        .option("user", "saveliy")
        .option("password", os.getenv("PSQL_BUSINESS_PSWD"))
        .mode("overwrite")
    )
    save_df.save()
    print(f"Done loading {num_lines}")
    ss.stop()
