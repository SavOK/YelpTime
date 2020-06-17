
# Sales Time

Insight Data Engineering Project  

**IMPORTANT** Before doing anything need to setup `config.py`

## Problem

### Data Source
List of Licenced business comes from Data.gov

**TODO** Insert data flow pickture

### Approach
* Process data with PySpark (clean and normolized) 
* Store data in Postgres 
* Use PostGIST to index spacial data (location)
* Dash UI to interact with data

Cleaning Data 
* Data saved at S3 as 94 csv files
* remove row without location coordinates, address, or industry description (NAICS number)
* if provided with number of employees broke number in bins (0-10, 10-100, 100-500, ...)
* if provided with sales value broke number in binss (0-1000, 1000-10000, 100000-500000, ...)

Storing Data
**TODO** insert Database schema

Calculating route time
* Here API

UI Dash app
* options State, 
* options business type
* transprotation mode
* time radius
* map starting loction input

### Project tree
+-- src
|   +-- SQL
|		+-- `__init__.py`
|		+-- `base.py`
|		+-- `BussinessTable.py`
|		+-- `CategoryTabel.py`
|		+-- `LocationTable.py`
|		+-- `AssociationTables.py`
|   +-- API
|		+-- `base.py`
|		+-- `BusinessTable.py`
|		+-- `CategoryTable.py`
|		+-- `LocationTable.py`
|	+-- assets
|   +-- `pyspark_clean_data.py`
|   +-- `help_functions_app.py`
|   +-- `main_app.py`
|   +-- `config.py`
+-- data
+-- `README.md`


### Done with help of 
`sqlalchemy`

