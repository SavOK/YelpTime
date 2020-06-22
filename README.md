
# Sales Time

Insight Data Engineering Project  

**IMPORTANT** Before doing anything need to setup `config.py`

## Problem

### Data Source
List of Licensed business comes from Data.gov

**TODO** Insert data flow picture

### Approach
* Process data with PySpark (clean and normalized) 
* Store data in Postgres 
* Use PostGIST to index spacial data (location)
* Dash UI to interact with data

Cleaning Data 
* Data saved at S3 as 94 csv files
* remove row without location coordinates, address, or industry description (NAICS number)
* if provided with number of employees, broke number in bins (0-10, 10-100, 100-500, ...)
* if provided with sales value, broke number in bins (0-1000, 1000-10000, 100000-500000, ...)

Storing Data
**TODO** insert Database schema

Calculating route time
* Here API

UI Dash app
* options State, 
* options business type
* transprotation mode
* time radius
* starting location

### Requirements
`boto3`== 1.13.25,
`dash`==1.12.0,
`GeoAlchemy2`==0.8.3,
`gunicorn`==20.0.4, 
`pandas`==1.0.4,
`psycopg2-binary`==2.8.5, 
`requests`==2.20.1, 
`SQLAlchemy`==1.3.17
### Project tree
./  
├── `LICENSE`  
├── `README.md`  
├── `config.py`  
├── data  
│&emsp;└── `6-digit_2017_Codes.csv`  
└── src  
&emsp;├── APIs  
&emsp;│ &emsp; ├── `HereAPI.py`  
&emsp;│ &emsp; └── `YelpAPI.py`  
&emsp;├── AirFlow  
&emsp;│ &emsp; └── `UpdateDataSchedule.py`  
&emsp;├── SQL  
&emsp;│ &emsp; ├── `AssociationTables.py`  
&emsp;│ &emsp; ├── `BusinessTable.py`  
&emsp;│ &emsp; ├── `CategoryTable.py`  
&emsp;│ &emsp; ├── `LocationTable.py`  
&emsp;│ &emsp; ├── `MainTable.py`  
&emsp;│ &emsp; ├── `__init__.py`  
&emsp;│ &emsp; └── `base.py`  
&emsp;├── SQLScripts    
&emsp;│ &emsp;└── `create_index.sql`   
&emsp;├── assets  
&emsp;│ &emsp; ├── `base.css`   
&emsp;│ &emsp; └── `style.css`  
&emsp;├── `config.py`  
&emsp;├── `help_functions_app.py`  
&emsp;├── `main_app.py`  
&emsp;└── `pyspark_clean_data.py`  

   
