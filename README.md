
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

### Project tree
YelpTime/  
├── `LICENSE`    
├── `README.md`   
├── `config.py`  
├── data  
│&emsp;├── `6-digit_2017_Codes.csv`  
└── src  
    ├── APIs  
    │&emsp;├── `HereAPI.py`  
    │&emsp;├── `YelpAPI.py`  
    │&emsp;└── `__init__.py`  
    ├── SQL  
    │&emsp;├── `AssociationTables.py`   
    │&emsp;├── `BusinessTable.py`  
    │&emsp;├── `CategoryTable.py`  
    │&emsp;├── `LocationTable.py`  
    │&emsp;├── `__init__.py`  
    │&emsp;└── `base.py`    
    ├── assets  
    │&emsp;├── `base.css`  
    │&emsp;└── `style.css`      
    ├── `config.py`   
    ├── `help_functions_app.py`    
    ├── `main_app.py`  
    └── `pyspark_clean_data.py`  
   

### Done with help of 
`sqlalchemy`

