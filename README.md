
# YelpTime

Insight Data Engineering Project  

**IMPORTANT** Before doing anything need to setup `config.py`

### Yelp data: get the list of business in Boston  

#### Approach
Run API search query to get a list of businesses around the point 
* iterate over 20km by 20km grid with the step 250m
* find all business around a point within 250m
* *Problems*: 
	* The distance yelp returns is approximation, number of businesses for each point varies from 0 to 4000.      

Build SQL wrapper to store data in PostgreSQL
* SQL Alchemy wrapper to interact with psql
* **TODO**  include tables shema in description
* Store location data in PostGIS

### Get distance information from [here.com](https://developer.here.com/)  
Run API to get POLYGON around the point of interest that could be reached in a time limit  
Based on POLYGON get locations that are inside the polygon and of the type `pizza` (for now)  
Run API to get the time and real road distance to the locations
Sort businesses based on the estimated time to reach  
**TODO** make location type an option

### Make Dash interactive web app
### Scale
