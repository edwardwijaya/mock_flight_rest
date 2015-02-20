Aggregating On-time Flight Data
================================
This is an implementation of RESTless API using Flask framework for a job application in Skyscanner.

Based on
--------

- Python
- Flask Framework

Guide
-----

- [Designing a RESTful API with Python and Flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)
- [Writing a Javascript REST client](http://blog.miguelgrinberg.com/post/writing-a-javascript-rest-client)
- [Designing a RESTful API using Flask-RESTful](http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful)

Setup
-----

- Install Python 2.7 and git.
- Run `setup.sh` (Linux, OS X, Cygwin) or `setup.bat` (Windows)
- Run `./skyscanner_rest_flightr.py` to start the server (on Windows use `flask\Scripts\python skyscanner_rest_flight.py` instead)
- Open `http://localhost:5000/index.html` on your web browser to run the client

GET http://localhost:5000/cancellation_pct/origin/LAX				--	List down all cancelled flights from <origin>
GET http://localhost:5000/cancellation_pct/origin/LAX??groupby=x 	--	List down cancelled flights probability from <origin> Grouped by <x>
E.g. (allowed group is [dest, distance, day_of_week, unique_carrier])
-	http://localhost:5000/cancellation_pct/origin/LAX?groupby=dest 
-	http://localhost:5000/cancellation_pct/origin/LAX?groupby=dest&groupby=distance&groupby=day_of_week&groupby=unique_carrier

GET http://localhost:5000/arrival_delay/origin/LAX					--	List down all flights from <origin>
GET http://localhost:5000/arrival_delay/origin/LAX??groupby=x 		--	List down all flights from <origin> and Grouped by <x>
E.g. (allowed group is [dest, distance, day_of_week, unique_carrier])
-	http://localhost:5000/arrival_delay/origin/LAX?groupby=distance
-	http://localhost:5000/arrival_delay/origin/LAX?groupby=dest&groupby=distance
