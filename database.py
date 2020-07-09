import pyodbc
from elements import Event, MeetupGroup
from tables import MeetupTable
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import os
import requests
from geopy.distance import distance
import numpy as np
from flask import request

DEFAULT_AFTER_DATE = date.today().strftime("%Y-%m-%d")
DEFAULT_BEFORE_DATE = "2022-12-31"
BEARINGS = [0, 90, 180, 270]


def connect_database():
    # connection_string = os.environ["SQLAZURECONNSTR_python"]
    connection_string = ***REMOVED***
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    return connection, cursor


def execute_command(cursor, command):
    cursor.execute(command)


def event_date(date, separator, default):
    if date['day'] != '0' or date['month'] != '0' or date['year'] != '0':
        day = date['day'] if date['day'] != '0' else "01"
        month = date['month'] if date['month'] != '0' else "01"
        year = date['year'] if date['year'] != '0' else "2020"
        return separator.join([year, month, day])
    return default


def event_genre(genre):
    if genre is not None and len(genre) != 0:
        return " AND B.genre_name='" + genre + "'"
    return ""


def event_distance(radius, location):
    if radius > 0:
        ranges = [distance(miles=radius).destination(location, b) for b in BEARINGS]
        latitude_range = np.array([i[0] for i in ranges])
        longitude_range = np.array([i[1] for i in ranges])
        min_latitude, max_latitude = np.min(latitude_range), np.max(latitude_range)
        min_longitude, max_longitude = np.min(longitude_range), np.max(longitude_range)
        distance_string = " AND B.latitude BETWEEN " + str(min_latitude) + " AND " + str(max_latitude) + \
                          " AND B.longitude BETWEEN " + str(min_longitude) + " AND " + str(max_longitude)
        return distance_string
    return ""


def get_events_command_construction(genre, events_after, events_before, radius, location):
    command = """SELECT DISTINCT B.event_name, B.event_date, B.venue_name, B.city, B.state, B.genre_name, B.url,
                            B.latitude, B.longitude, A.attraction_name 
                            FROM ticketmaster_attractions AS A
                            INNER JOIN ticketmaster_events AS B
                            ON A.attraction_id = B.attraction_id
                            WHERE city=? AND state=? 
                            AND B.event_date BETWEEN ? AND ?
                    """
    separator = '-'
    after_date = event_date(events_after, separator, DEFAULT_AFTER_DATE)
    before_date = event_date(events_before, separator, DEFAULT_BEFORE_DATE)
    distance_string = event_distance(radius, location)
    order = " ORDER BY B.event_date"
    genre_string = event_genre(genre)
    command = command + genre_string + distance_string + order
    return command, after_date, before_date


def get_events(city, state, genre, events_after, events_before, radius, location):
    command, after_date, before_date = get_events_command_construction(genre, events_after, events_before, radius, location)
    connection, cursor = connect_database()
    cursor.execute(command, city, state, after_date, before_date)
    rows = cursor.fetchall()
    executor = ThreadPoolExecutor(max_workers=5)
    futures = executor.map(process_event, rows)
    events = []
    for event in futures:
        events.append(event)
    connection.close()
    return events


def process_event(row):
    connection, cursor = connect_database()
    venue_map = "https://maps.google.com/?q="
    zoom = "&z=8"
    event_date = row.event_date.date()
    venue = row.venue_name
    genre = row.genre_name
    latitude = row.latitude
    longitude = row.longitude
    artist = row.attraction_name
    artist_url = row.url
    venue_url = venue_map + str(latitude) + "," + str(longitude) + zoom
    city = row.city
    state = row.state
    meetup_groups = get_groups(city, state, artist, genre, venue, cursor)
    event = Event(event_date, artist, artist_url, venue, venue_url, genre, meetup_groups)
    connection.close()
    return event


def multiple_genres(genre, command):
    if genre.lower().find('/') != -1:
        separate = genre.lower().split('/')
        for each in separate:
            new_genre = "'%" + each + "%'"
            command = command + " OR A.group_name like " + new_genre
    elif genre == "R&B":
        command = command + " OR A.group_name like '%rhythm%' OR A.group_name like '%blues%'"
    return command


def get_groups_command_construction(artist, genre, venue):
    artist = "%" + artist + "%"
    genre = "%" + genre + "%"
    venue = "%" + venue + "%"
    command = """SELECT DISTINCT * FROM (
                    SELECT group_name, url FROM meetup_groups
                    WHERE city = ? AND state = ?) AS A
                    WHERE A.group_name like ?
                    OR A.group_name like ?
                    OR A.group_name like ?
            """
    command = multiple_genres(genre, command)
    return command, artist, genre, venue


def default_get_groups_command_construction():
    command = """SELECT DISTINCT * FROM (
                        SELECT group_name, url FROM meetup_groups
                        WHERE city = ? AND state = ?) AS A
                        WHERE A.group_name LIKE '%concert%'
                """
    return command


def process_group(row):
    name = row.group_name
    url = row.url
    group = MeetupGroup(name, url)
    return group


def get_groups(city, state, artist, genre, venue, cursor):
    command, artist, genre, venue = get_groups_command_construction(artist, genre, venue)
    cursor.execute(command, city, state, artist, genre, venue)
    rows = cursor.fetchall()
    if len(rows) < 1:
        command = default_get_groups_command_construction()
        rows = cursor.fetchall()
        cursor.execute(command, city, state)
    groups = []
    executor = ThreadPoolExecutor(max_workers=5)
    futures = executor.map(process_group, rows)
    for group in futures:
        groups.append(group)
    return MeetupTable(groups)


def get_coordinates():
    ip_address = requests.get('https://api.ipify.org').text
    response = requests.get("http://ip-api.com/json/{}".format(ip_address))
    result = response.json()
    latitude = result["lat"]
    longitude = result["lon"]
    return latitude, longitude

