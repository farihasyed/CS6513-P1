import requests
import os
import time
from multiprocessing import Pool
from database_operations import connect_database, close_database

# EXAMPLE https://api.meetup.com/find/groups?&country=US&category=21&access_token=******
MEETUP_BASE_URL = 'https://api.meetup.com/find/groups?'
MEETUP_OAUTH_ACCESS_TOKEN = '&access_token=' + os.environ['MEETUP_KEY']
MEETUP_LOCATION = '&location='
MEETUP_MUSIC_CATEGORY_ID = '&category=21'
MEETUP_COUNTRY = '&country=US'
connection, cursor = connect_database()
groups_ = []


def scrape_meetup_groups(location):
    print("Scraping Meetup groups from {}".format(location[0]))
    city_name = process_city_name(location[0])
    link = MEETUP_BASE_URL + MEETUP_COUNTRY + MEETUP_MUSIC_CATEGORY_ID + MEETUP_LOCATION + city_name \
          + MEETUP_OAUTH_ACCESS_TOKEN
    response = requests.get(link, verify=False)
    data = response.json()
    if response.status_code == requests.codes.ok:
        for group in data:
            group_id = str(group['id'])
            group_name = group['name']
            city = group['city']
            state = group['state']
            url = group['link']
            latitude = str(group['lat'])
            longitude = str(group['lon'])
            group_ = ','.join([group_id, group_name, city, state, url, latitude, longitude])
            groups_.append(group_)
        # Meetup's API limits numbers of requests to 30/hour, so sleep for 20 minutes because 10 threads
        time.sleep(1200)
    return '\n'.join(groups_)


def get_ticketmaster_locations():
    cursor.execute('SELECT DISTINCT city FROM ticketmaster_events')
    return cursor.fetchall()


def process_city_name(location):
    city_name = location[0].lstrip()
    if city_name.find(' ') != -1:
        city_name = city_name.replace(" ", "+")
    return city_name


def meetup():
    locations = get_ticketmaster_locations()
    close_database(connection)
    with Pool(10) as p:
        groups = p.map(scrape_meetup_groups, locations)
    with open("meetup_groups.txt", "w+") as file:
        file.write(''.join(groups))
    file.close()


meetup()
