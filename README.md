
# Sales Time

Insight Data Engineering Project  

**IMPORTANT** Before doing anything need to setup `config.py`

## Problem

### Data Flow
![Data Flow][flow]

### Data Source
List of Licensed business comes from Data.gov

### Approach
* Process data with PySpark (clean and normalized) 
* Store data in Postgre 
* Use PostGIST to index spacial data (location)
* Dash UI to interact with data

Cleaning Data 
* Data saved at S3 as 51 csv files
* Remove row without location coordinates, address, or industry description (NAICS number)
* If provided with number of employees, broke number in bins (0-10, 10-100, 100-500, ...)
* If provided with sales value, broke number in bins (0-1000, 1000-10000, 100000-500000, ...)

Storing Data  
* Clean and normalized data stored
![Database schema][schema]

Calculating route time
* Here API

UI Dash app
* options State, 
* options Business type
* Transportation mode
* Time radius
* Starting location

### Requirements
`boto3`, 
`dash`, 
`GeoAlchemy2`, 
`gunicorn`,
`pandas`, 
`psycopg2-binary`,
`requests`,
`SQLAlchemy`
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

[flow]: images/data_flow.png "Data Flow"
[schema]:  ./images/schema.png "DB Schema"
