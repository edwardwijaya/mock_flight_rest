#!flask/bin/python
# Copyright (C) 2015 Edward Wijaya
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This is a REST API server that runs for Skyscanner On Time Flight Data

Available API to use are :
- GET / (for the list of flights)
- GET /arrival_delay/origin/<origin>
- GET /arrival_delay/origin/<origin>?groupby=<group>
- GET /cancellation_pct/origin/<origin>
- GET /cancellation_pct/origin/<origin>?groupby=<group_key>

The source code PEP8 compliant.

"""

import json
from collections import defaultdict
from urlparse import urlparse
from urlparse import parse_qsl
from flask import Flask
from flask import jsonify
from flask import abort
from flask import request
from flask import make_response

app = Flask(__name__, static_url_path="")
json_data = open('data/ontime_data_test.json')
flights_data = json.load(json_data)

distance_range = 100  # segmentation every distance range
allowed_group = {'dest': "Destination",
                 'unique_carrier': "Flight_Carrier",
                 'day_of_week': "Day_of_the_Week",
                 'distance': "Distance"}

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


@app.route('/', methods=['GET'])
def get_flights():
    """
    This returns a JSON formatted list of flights data with each attribute.
    :return: List of flights in JSON format
    """
    return jsonify({'flights_data': [make_public_flight(flight) for flight in flights_data]})


@app.route('/arrival_delay/origin/<origin>', methods=['GET'])
def get_arrival_delay(origin):
    """
    Shows the summary of time delay of flights flying from an <origin> airport.
    Time of delay returned in "<mininum> - <maximum> minute(s) late" format.
    Unit of time used are minutes.
    Group can be used to categorize the arrival delay.

    :param origin: Origin of airport to check the arrival delay
    :return: Overall arrival delay in JSON format
    """

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

    # Make a list of flights originated from <origin>
    flights_from_origin = []
    for flight in flights_data:
        if flight['origin'] == origin:
            flights_from_origin.append(flight)
    if len(flights_from_origin) == 0:
        abort(404)

    # GET /arrival_delay/origin/<origin> - No query parameters
    if not query_string:
        overall_delay = []
        for flight in flights_from_origin:
            time_of_arrival = int(flight['arr_delay']) if flight['arr_delay'] else None
            if time_of_arrival is not None and time_of_arrival < 0:
                overall_delay.append(time_of_arrival)

        earliest_delay = str(abs(max(overall_delay)))
        longest_delay = str(abs(min(overall_delay)))
        return jsonify(
                {'Flying_from': str(origin),
                 'Output - Expected time of Arrival Delay': earliest_delay + " - " + longest_delay + " minute(s) late"})

    # GET /arrival_delay/origin/<origin>?groupby=<group_key>
    else:
        flights_dictionaries = {'Flying_from': str(origin)}

        # Iterate from list of group query
        for query_key in group_keys:
            flights_dictionaries['Output - Expected time of Arrival Delay - Group: ' + allowed_group.get(query_key)] \
                = group_delay(query_key, flights_from_origin)

        return jsonify(flights_dictionaries)

@app.route('/cancellation_pct/origin/<origin>', methods=['GET'])
def get_cancellation_pct(origin):
    """
    Shows the percentage of cancelled flights flying from an <origin> airport.
    Cancelled flights are calculated from no. of cancelled flights / the total of flights.
    Returns a percentage of flight cancellation possibility.
    Group can be used to categorize the cancelled flights.

    :param origin: Origin of airport to check the arrival delay
    :return: Percentage of cancelled flights in JSON format
    """
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

    # Make a list of flights originated from <origin>
    flights = []
    for flight in flights_data:
        if flight['origin'].lower() == origin.lower():
            flights.append(flight)
    if len(flights) == 0:
        abort(404)

    # GET /cancellation_pct/origin/<origin> - No query parameters
    if not query_string:
        flight_dictionaries = {'Flying_from': str(origin)}
        cancellations_amt = 0.0

        for flight in flights:
            for field in flight:
                if field == "cancelled":
                    if int(flight[field]) == 1:
                        cancellations_amt += 1

        cancellations_pct = float(cancellations_amt) / len(flights)
        flight_dictionaries['Output - Cancelled Possibility'] = str(("%.2f" % round(cancellations_pct,2)))
        return jsonify(flight_dictionaries)

    # GET /cancellation_pct/origin/<origin>?groupby=<group_key>
    else:
        flight_dictionaries = {'Flying_from': str(origin)}

        # Iterate from list of group query
        for group_key in group_keys:
            flight_dictionaries['Output - Cancellation Possibility - Group: ' + allowed_group.get(group_key)] = \
                group_cancel(group_key, flights)

        return jsonify(flight_dictionaries)


def group_delay(group_key, flights):
    """
    Group the arrival delay flights based on keys.
    :param group_key: Group key to use for categorization.
    :param flights: List of flights matching from an origin airport.
    :return: Dictionary containing the list of flights grouped.
    """
    dict_of_group_flights = defaultdict(list)

    if group_key == 'distance':
        global distance_range   # segmentation every distance range

        # Remove duplicate value & Get the maximum distance
        distance_set = set()
        for flight in flights:
            distance_set.add(int(flight['distance']))

        distance_list = sorted(list(distance_set))
        max_distance = max(distance_list)

        # Segment into Ranges
        temp_dict = defaultdict(list)
        for flight in flights:
            distance_limit = 0
            while distance_limit <= max_distance:
                if int(flight[group_key]) in range(distance_limit, distance_limit + distance_range):
                    time_of_arrival = int(flight['arr_delay']) if flight['arr_delay'] else None
                    if time_of_arrival is not None and time_of_arrival < 0:
                        distance_ranges = str(distance_limit) + " - " + str(distance_limit + distance_range) + " miles"
                        temp_dict[distance_ranges].append(time_of_arrival)
                distance_limit += distance_range

    elif group_key == 'day_of_week':
        temp_dict = defaultdict(list)
        for flight in flights:
            time_of_arrival = int(flight['arr_delay']) if flight['arr_delay'] else None
            if time_of_arrival is not None and time_of_arrival < 0:
                name_of_day = get_day_name(int(flight[group_key]))
                temp_dict[name_of_day].append(time_of_arrival)

    else:
        temp_dict = defaultdict(list)
        for flight in flights:
            time_of_arrival = int(flight['arr_delay']) if flight['arr_delay'] else None
            if time_of_arrival is not None and time_of_arrival < 0:
                temp_dict[flight[group_key]].append(time_of_arrival)

    # Overall Arrival Delay in "<minimum> - <maximum> minute(s) late" format
    for key, delay_list in temp_dict.iteritems():
        fastest_delay = str(abs(max(delay_list)))
        longest_delay = str(abs(min(delay_list)))
        if fastest_delay == longest_delay:
            dict_of_group_flights[key].append(fastest_delay + " minute(s) late")
        else:
            dict_of_group_flights[key].append(fastest_delay + " - " + longest_delay + " minute(s) late")

    return dict_of_group_flights


def group_cancel(group_key, flights):
    """
    Group the cancelled flights based on keys.
    :param group_key: Group key to use for categorization.
    :param flights: List of flights matching from an origin airport.
    :return: Dictionary containing the list of flights grouped.
    """
    dict_of_group_flights = defaultdict(list)

    if group_key == 'distance':
        global distance_range   # segmentation every distance range

        # Remove duplicate value & Get the maximum distance
        distance_set = set()
        for flight in flights:
            distance_set.add(int(flight['distance']))

        distance_list = sorted(list(distance_set))
        max_distance = max(distance_list)

        # Segment into Ranges
        temp_dict = defaultdict(list)
        for flight in flights:
            distance_limit = 0
            while distance_limit <= max_distance:
                if int(flight[group_key]) in range(distance_limit, distance_limit + distance_range):
                    distance_ranges = str(distance_limit) + " - " + str(distance_limit + distance_range) + " miles"
                    temp_dict[distance_ranges].append(int(flight['cancelled']))
                distance_limit += distance_range

    elif group_key == 'day_of_week':
        temp_dict = defaultdict(list)
        for flight in flights:
            name_of_day = get_day_name(int(flight[group_key]))
            temp_dict[name_of_day].append(int(flight['cancelled']))

    else:
        temp_dict = defaultdict(list)
        for flight in flights:
            temp_dict[flight[group_key]].append(int(flight['cancelled']))

    # Calculate the cancellation percentage
    for key, cancellation_list in temp_dict.iteritems():
        cancellation_amount = list(cancellation_list).count(1)
        cancellation_percentage = float(cancellation_amount) / len(cancellation_list)
        dict_of_group_flights[key].append(str(("%.2f" % round(cancellation_percentage, 2))))

    return dict_of_group_flights

def get_day_name(day_no):
    """
    Returns the full name of the day in the week.
    :param day_no: The number of day to convert.
    :return: Full name of day in the week.
    """
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

    return "NOT_RECOGNIZED"

if __name__ == '__main__':
    app.run(debug=True)
