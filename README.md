
# Sales Time
**Insight Data Engineering Project**

The idea is to provide recommendations to door-to-door sales which potential customer to visit next. Given the stringent time-limit, the sales person would want to know the customer fastest to reach. The app suggests next location to visit based on mode of transportation and real-time road conditions 


### Table of Contents
**[Data Flow](#data-flow)**<br/>
**[Data Source](#data-source)**<br/>
**[Approach](#approach)**<br/>
* **[Cleaning Data](#cleaning-data)**</br>
* **[Storing Data](#storing-data)**</br>
* **[Calculating Route Time](#calculating-route-time)**</br>
* **[UI Dash App](#ui-dash-app)**</br>
  
**[Installation and Usage](#installation-and-usage)**<br/>

## Data Flow
![Data Flow][flow]

## Data Source
List of Licensed business comes from Data.gov

## Approach
* Process data with PySpark (clean and normalize) 
* Store data in Postgres 
* Use PostGIST to index spacial data (location)
* Dash UI to interact with data

### Cleaning Data 
* Data saved at S3 as 51 csv files
* Removed row without location coordinates, address, or industry description (NAICS number)
* If provided with number of employees, broke number in bins (0-10, 10-100, 100-500, ...)
* If provided with sales value, broke number in bins (0-1000, 1000-10000, 100000-500000, ...)

### Storing Data  
* Cleaned and normalized data stored
![Database schema][schema]

### Calculating Route Time
* Here API

### UI Dash App
* options State 
* options Business type
* Transportation mode
* Time radius
* Starting location

## Installation and Usage
**IMPORTANT** Before doing anything need to setup `config.py`
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
