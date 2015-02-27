Aggregating On-time Flight Data
================================
This is an implementation of RESTless API using Flask framework for a job application in Skyscanner.

Question:
Based on the JSON data(ontime_data_test.json). Suppose you are building a backend for a flight delay visualization application. Your goal is to build an API exposing the attached information to answer the following questions:
  1.	What is the expected arrival delay when flying from a specific airport grouped by any or all of the following:
    a.	Arrival Airport?
    b.	Carrier?
    c.	Distance (segmented into ranges as appropriate)?
    d.	Day of the Week?
  2.	What is the likelihood of a flight being cancelled when flying from a specific airport grouped by any or all of the following:
    a.	Arrival Airport?
    b.	Carrier?
    c.	Distance (segmented into ranges as appropriate)?
    d.	Day of the Week?


Based on
--------

- [Python](https://www.python.org/)
- [Flask Framework](http://flask.pocoo.org/)

Guide
-----

- [Designing a RESTful API with Python and Flask](http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask)
- [Writing a Javascript REST client](http://blog.miguelgrinberg.com/post/writing-a-javascript-rest-client)
- [Designing a RESTful API using Flask-RESTful](http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful)

Setup
-----

- Install Python 2.7 and git.
- Run `setup.sh` (Linux, OS X, Cygwin) or `setup.bat` (Windows)
- Run `./skyscanner_rest_flight.py` to start the server (on Windows use `flask\Scripts\python skyscanner_rest_flight.py` instead)
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

Feedback
--------
- Good implementation with concise result.
- Were asked of the O(n) of the distance group mapping which is O(n) which can be improved to O(1) by using modulo operation
- Implementation using REST framework - Flask is a good choice
- PEP8 certified which is good, but overlooked.

The interviews was done and noted the good implementation, we went through with the discussion over technical interviews however the result came back with "technical experience does not fit well required for the role and product that are working on".
