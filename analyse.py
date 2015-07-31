#!/usr/bin/env python
#
# Copyright 2008-2009 TripIt, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

import tripit
from distance import haversine
from pprint import pprint

class Trip(object):
    def __init__(self, start_date, end_date, location, latitude, longitude):
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.latitude = latitude
        self.longitude = longitude

def main(argv):
    if len(argv) < 5:
        print "Usage: example.py api_url consumer_key consumer_secret authorized_token authorized_token_secret"
        return 1

    api_url = argv[0]
    consumer_key = argv[1]
    consumer_secret = argv[2]
    authorized_token = argv[3]
    authorized_token_secret = argv[4]

    oauth_credential = tripit.OAuthConsumerCredential(consumer_key, consumer_secret, authorized_token, authorized_token_secret)
    t = tripit.TripIt(oauth_credential, api_url = api_url)

    future_trips = t.list_trip({ 'past': 'false', 'page_size': 100 }).get_children()[:-1]
    past_trips = t.list_trip({ 'past': 'true', 'page_size': 100 }).get_children()[:-1]

    trips = []

    for trip in sorted(future_trips+past_trips):
        start_date = trip.get_attribute_value("start_date")

        # ignore all trips before going homeless
        if start_date.isoformat() < "2012-08-30":
            continue

        end_date = trip.get_attribute_value("end_date")
        location = trip.get_attribute_value("primary_location")
        primary_location = trip.get_children()[1]
        latitude = float(primary_location.get_attribute_value("latitude"))
        longitude = float(primary_location.get_attribute_value("longitude"))

        trip = Trip(start_date, end_date, location, latitude, longitude)
        trips.append(trip)

    # This all started from Edinburgh
    previous_trip = Trip(0, 0, "Edinburgh, United Kingdom", 55.9500, 3.2200)
    total_distance = 0

    print "To\tStart Date\tEnd Date\tTravelled distance"

    for trip in trips:
        distance = 0
        if previous_trip:
            distance = haversine(previous_trip.longitude, previous_trip.latitude, trip.longitude, trip.latitude)

        print "%s\t%s\t%s\t%s" % (trip.location, trip.start_date, trip.end_date, distance)

        previous_trip = trip
        total_distance += distance

    print "Total travelling distance %s" % total_distance

    print "<table>"
    print "<tr><td>To</td><td>Start Date</td><td>End Date</td><td>Travelled distance</td></tr>"

    for trip in trips:
        distance = 0
        if previous_trip:
            distance = haversine(previous_trip.longitude, previous_trip.latitude, trip.longitude, trip.latitude)

        print "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (trip.location, trip.start_date, trip.end_date, int(distance))

        previous_trip = trip
        total_distance += distance

    print "</table>"

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
