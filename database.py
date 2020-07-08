import pyodbc
from elements import Event, MeetupGroup
from tables import MeetupTable
from concurrent.futures import ThreadPoolExecutor
import os


def connect_database():
    connection_string = os.environ["SQLAZURECONNSTR_python"]
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    return connection, cursor


def execute_command(cursor, command):
    cursor.execute(command)


def get_events(city, state):
    command = """SELECT DISTINCT B.event_name, B.event_date, B.venue_name, B.city, B.state, B.genre_name, B.url,
                B.latitude, B.longitude, A.attraction_name 
                FROM ticketmaster_attractions AS A
                INNER JOIN ticketmaster_events AS B
                ON A.attraction_id = B.attraction_id
                WHERE city=? AND state=?
                AND B.event_date BETWEEN (SELECT GETDATE()) AND '2022-01-01'
                ORDER BY B.event_date
    """
    connection, cursor = connect_database()
    cursor.execute(command, city, state)
    rows = cursor.fetchall()
    executor = ThreadPoolExecutor(max_workers=5)
    futures = executor.map(process, rows)
    events = []
    for event in futures:
        events.append(event)
    return events


def process(row):
    connection, cursor = connect_database()
    venue_map = "https://maps.google.com/?q="
    ZOOM = "&z=8"
    date = row.event_date.date()
    venue = row.venue_name
    genre = row.genre_name
    latitude = row.latitude
    longitude = row.longitude
    artist = row.attraction_name
    artist_url = row.url
    venue_url = venue_map + str(latitude) + "," + str(longitude) + ZOOM
    city = row.city
    state = row.state
    meetup_groups = get_groups(city, state, artist, genre, venue, cursor)
    event = Event(date, artist, artist_url, venue, venue_url, genre, meetup_groups)
    connection.close()
    return event


def get_groups(city, state, artist, genre, venue, cursor):
    command = """SELECT DISTINCT * FROM (
                    SELECT group_name, url FROM meetup_groups
                    WHERE city = ? AND state = ?) AS A
                    WHERE A.group_name like ?
                    OR A.group_name like ?
                    OR A.group_name like ?
            """
    if genre.lower().find('/') != -1:
        separate = genre.lower().split('/')
        for each in separate:
            new_genre = """'%""" + each + """%'"""
            command = command + " OR A.group_name like " + new_genre
    cursor.execute(command, city, state, "%" + artist + "%", "%" + genre + "%", "%" + venue + "%")
    rows = cursor.fetchall()
    if len(rows) < 1:
        command = """SELECT DISTINCT * FROM (
                    SELECT group_name, url FROM meetup_groups
                    WHERE city = ? AND state = ?) AS A
                    WHERE A.group_name LIKE '%concert%'
            """
        cursor.execute(command, city, state)
        rows = cursor.fetchall()
    groups = []
    for row in rows:
        name = row.group_name
        url = row.url
        group = MeetupGroup(name, url)
        groups.append(group)
    return MeetupTable(groups)