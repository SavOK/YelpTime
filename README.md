# YelpTime

Insight Data Engineering Project  

**IMPORTANT** Before doing anything need to setup `config.py`
## Step 1: Get the data connect to API  

### Yelp data: get the list of bussness in Bonston  

#### Aproach
Run API search query to get list of businesses around point 
* iterate over 20km by 20km grid with the step 250m
* find all bussness around point within 250m
* *Problems*: 
	* Brute force didn't worked need to limit extraction by category
	* The distance yelp returns  is aproxmate number of busnesses for each point  not equaly spreaded.
	* **TODO**  Modifie queries so get businesses by category 
	
Build SQL wrapper to store data in PostgreSQL
* SQL Alchemy wrapper to interact with psql
* **TODO**  include tables shema in description
* Store location data in PostGIS
* **TODO** gist index locations

### Get distance information from [here.com](https://developer.here.com/)  
Run API to get POLYGON around point of interest that could be reached in time limit
