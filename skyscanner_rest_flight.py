#!flask/bin/python
import json
from collections import defaultdict
from urlparse import urlparse, parse_qsl
from flask import Flask, jsonify, abort, request, make_response

"""
This is a REST server that runs for Skyscanner On Time Flight Data
"""
app = Flask(__name__, static_url_path="")
json_data = open('ontime_data_test.json')
flights_data = json.load(json_data)
distance_range = 50  # in miles
allowed_group = {'dest': "Destination", 'unique_carrier': "Flight_Carrier",
                 'day_of_week': "Day_of_the_Week", 'distance': "Distance"}

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def make_public_flight(flight):
    new_flight = {}
    for field in flight:
        new_flight[field] = flight[field]
    return new_flight

def make_arrival_delay(flight, group_key):
    new_arrival_delay = {}
    for field in flight:
        """
        Field to display according to group key
        """
        if field == 'arr_delay':
            time_of_arrival = int(flight[field]) if flight[field] else None
            if time_of_arrival is None:
                new_arrival_delay['Time_of_arrival'] = 'NaN'
            elif time_of_arrival < 0:
                new_arrival_delay['Time_of_arrival'] = str(abs(time_of_arrival)) + ' minute(s) late'
            elif time_of_arrival > 0:
                new_arrival_delay['Time_of_arrival'] = str(time_of_arrival) + ' minute(s) early'
            elif time_of_arrival == 0:
                new_arrival_delay['Time_of_arrival'] = 'On_Time'

        if field == 'fl_date':
            new_arrival_delay['Date_of_flight'] = str(flight[field])
        if field == 'distance' and group_key == 'distance':
            new_arrival_delay['Distance'] = str(flight[field]) + " miles"
    return new_arrival_delay

def make_cancellation_pct(flight):
    cancellations_pct = {}
    if str(flight['cancelled']) == "1":
        for field in flight:
            if field == 'cancelled':
                cancelled = bool(int(flight[field]))
                cancellations_pct['Cancelled'] = cancelled
            else:
                cancellations_pct[field] = flight[field]

        return cancellations_pct
    else:
        return None

@app.route('/', methods=['GET'])
def get_flights():
    return jsonify({'flights_data': [make_public_flight(flight) for flight in flights_data]})

@app.route('/arrival_delay/origin/<origin>', methods=['GET'])
def get_arrival_delay(origin):
    # Parse using urlparse to retrieve query string for GROUP separation [1]
    # [1] : https://docs.python.org/2/library/urlparse.html#urlparse.urlparse
    query_string = parse_qsl(urlparse(request.url).query)

    # Filter out query string parameters
    # Process the queries parameter feed
    # For now, only take the 'groupby' parameter
    group_keys = set()
    allowed_group_keys = allowed_group.keys()

    for query, query_value in query_string:
        if query == "groupby":
            if query_value in allowed_group_keys:  # matched the group allowed
                group_keys.add(query_value)

    flights = []
    for flight in flights_data:
        if flight['origin'].lower() == origin.lower():
            flights.append(flight)
    if len(flights) == 0:
        abort(404)
    if len(group_keys) == 0:
        abort(400)

    if not query_string:
        return jsonify(
            {'Flying_from': str(origin),
             'Output - Time_of_Arrival': [make_arrival_delay(flight, None) for flight in flights]})
    else:
        flights_dictionaries = {'Flying_from': str(origin)}

        # Iterate from list of queries
        # [1] Group queries
        for query_key in group_keys:
            flights_dictionaries['Output - Time_of_Arrival - Group: ' + allowed_group.get(query_key)] \
                = group_delay(query_key, flights)

        return jsonify(flights_dictionaries)

@app.route('/cancellation_pct/origin/<origin>', methods=['GET'])
def get_cancellation_pct(origin):
    # Parse using urlparse to retrieve query string for GROUP separation [1]
    # [1] : https://docs.python.org/2/library/urlparse.html#urlparse.urlparse
    query_string = parse_qsl(urlparse(request.url).query)

    # Filter out query string parameters
    # Process the queries parameter feed
    # For now, only take the 'groupby' parameter
    group_keys = set()
    allowed_group_keys = allowed_group.keys()

    for query, query_value in query_string:
        if query == "groupby":
            if query_value in allowed_group_keys:  # matched the group allowed
                group_keys.add(query_value)

    flights = []
    for flight in flights_data:
        if flight['origin'].lower() == origin.lower():
            flights.append(flight)
    if len(flights) == 0:
        abort(404)
    if len(group_keys) == 0:
        abort(400)

    if not query_string:
        flight_dictionaries = {'Flying_from': str(origin)}
        flight_list = []
        for flight in flights:
            flight_data = make_cancellation_pct(flight)
            if flight_data is not None:
                flight_list.append(flight_data)

            flight_dictionaries['Output - Cancelled Flights List'] = flight_list
        return jsonify(flight_dictionaries)
    else:
        flight_dictionaries = {'Flying_from': str(origin)}

        # Iterate from list of queries
        # [1] Group queries
        for group_key in group_keys:
            flight_dictionaries['Output - Cancellation Possibility - Group: ' + allowed_group.get(group_key)] = \
                group_cancel(group_key, flights)

        return jsonify(flight_dictionaries)

def group_delay(group_key, flights):
    dict_of_group_flights = defaultdict(list)

    if group_key == 'distance':
        global distance_range
        distance_set = set()    # filter duplicate value
        for flight in flights:
            distance_set.add(int(flight['distance']))

        distance_list = sorted(list(distance_set))
        max_distance = max(distance_list)

        for flight in flights:
            distance_limit = 0
            while distance_limit <= max_distance:
                if int(flight[group_key]) in range(distance_limit, distance_limit + distance_range):
                    distance_ranges = str(distance_limit) + " - " + str(distance_limit + distance_range)
                    dict_of_group_flights[distance_ranges].append(make_arrival_delay(flight, group_key))
                distance_limit += distance_range
    elif group_key == 'day_of_week':
        for flight in flights:
            name_of_day = get_day_name(int(flight[group_key]))
            dict_of_group_flights[name_of_day].append(make_arrival_delay(flight, group_key))

    else:
        for flight in flights:
            dict_of_group_flights[flight[group_key]].append(make_arrival_delay(flight, group_key))

    return dict_of_group_flights

def group_cancel(group_key, flights):
    dict_of_group_flights = defaultdict(list)

    if group_key == 'distance':
        global distance_range
        distance_set = set()    # filter duplicate value
        for flight in flights:
            distance_set.add(int(flight['distance']))

        distance_list = sorted(list(distance_set))
        max_distance = max(distance_list)

        temp_dict = defaultdict(list)
        for flight in flights:
            distance_limit = 0
            while distance_limit <= max_distance:
                if int(flight[group_key]) in range(distance_limit, distance_limit + distance_range):
                    distance_ranges = str(distance_limit) + " - " + str(distance_limit + distance_range)
                    temp_dict[distance_ranges].append(int(flight['cancelled']))
                distance_limit += distance_range

        for distance_ranges, cancellation_list in temp_dict.iteritems():
            cancellation_amount = list(cancellation_list).count(1)
            cancellation_percentage = float(cancellation_amount) / len(cancellation_list)
            dict_of_group_flights[distance_ranges].append(cancellation_percentage)

    elif group_key == 'day_of_week':
        temp_dict = defaultdict(list)
        for flight in flights:
            name_of_day = get_day_name(int(flight[group_key]))
            temp_dict[name_of_day].append(int(flight['cancelled']))

        for name_of_day, cancellation_list in temp_dict.iteritems():
            cancellation_amount = list(cancellation_list).count(1)
            cancellation_percentage = float(cancellation_amount) / len(cancellation_list)
            dict_of_group_flights[name_of_day].append(cancellation_percentage)

    else:
        temp_dict = defaultdict(list)
        for flight in flights:
            temp_dict[flight[group_key]].append(int(flight['cancelled']))

        for key, cancellation_list in temp_dict.iteritems():
            cancellation_amount = list(cancellation_list).count(1)
            cancellation_percentage = float(cancellation_amount) / len(cancellation_list)
            dict_of_group_flights[key].append(cancellation_percentage)

    return dict_of_group_flights

def get_day_name(day_no):
        if day_no == 1:
            return "Monday"
        elif day_no == 2:
            return "Tuesday"
        elif day_no == 3:
            return "Wednesday"
        elif day_no == 4:
            return "Thursday"
        elif day_no == 5:
            return "Thursday"
        elif day_no == 6:
            return "Saturday"
        elif day_no == 7:
            return "Sunday"
        else:
            return "NOT_RECOGNIZED"
if __name__ == '__main__':
    app.run(debug=True)
	