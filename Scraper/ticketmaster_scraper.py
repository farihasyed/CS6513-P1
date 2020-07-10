import requests
from database import connect_database, close_database
from multiprocessing import Pool
import os

# EXAMPLE https://app.ticketmaster.com/discovery/v2/attractions.json?size=1&apikey=******
TICKETMASTER_BASE_URL = 'https://app.ticketmaster.com/discovery/v2/'
TICKETMASTER_SOURCE = 'source=ticketmaster'
TICKETMASTER_COUNTRY_CODE = '&countryCode=US'
TICKETMASTER_KEY = '&apikey=' + os.environ['TICKETMASTER_KEY']
TICKETMASTER_DMA_ID = '&dmaId='
TICKETMASTER_JSON = '.json?'
TICKETMASTER_EVENT_OBJECT = 'events'
TICKETMASTER_MUSIC_CLASSIFICATION_ID = '&classificationId=KZFzniwnSyZfZ7v7nJ'
TICKETMASTER_ATTRACTION_OBJECT = 'attractions/'
TICKETMASTER_ATTRACTION_ID = '&id='
connection, cursor = connect_database()
events_ = []
attractions_ = []


def get_ticketmaster_dmas():
    cursor.execute("SELECT id FROM dma WHERE id < 500")
    return cursor.fetchall()


def get_ticketmaster_attraction_ids():
    cursor.execute("SELECT DISTINCT attraction_id FROM ticketmaster_events")
    return cursor.fetchall()


def scrape_ticketmaster_events(dma):
    print("Scraping events from dma = {}".format(dma[0]))
    link = TICKETMASTER_BASE_URL + TICKETMASTER_EVENT_OBJECT + TICKETMASTER_JSON + TICKETMASTER_SOURCE + \
          TICKETMASTER_COUNTRY_CODE + TICKETMASTER_DMA_ID + str(dma[0]) + \
          TICKETMASTER_MUSIC_CLASSIFICATION_ID + TICKETMASTER_KEY
    response = requests.get(link)
    data = response.json()
    if response.status_code == requests.codes.ok:
        for event in data['_embedded']['events']:
            event_id = event['id']
            event_name = event['name']
            event_date = event['dates']['start']['localDate']
            attraction_id = event['_embedded']['attractions'][0]['id'] if ('attractions' in event['_embedded']) \
                else 'N/A'
            venue_id = event['_embedded']['venues'][0]['id']
            venue_name = event['_embedded']['venues'][0]['name']
            city = event['_embedded']['venues'][0]['city']['name']
            state = event['_embedded']['venues'][0]['state']['name']
            country = event['_embedded']['venues'][0]['country']['countryCode']
            if 'location' in event['_embedded']['venues'][0]:
                latitude = event['_embedded']['venues'][0]['location']['latitude']
                longitude = event['_embedded']['venues'][0]['location']['longitude']
            else:
                latitude = 99999
                longitude = 99999
            genre_id = event['classifications'][0]['genre']['id']
            genre_name = event['classifications'][0]['genre']['name']
            url = event['url']
            event = ','.join([event_id, event_name, event_date, attraction_id, venue_id, venue_name, city, state,
                              country, str(latitude), str(longitude), genre_id, genre_name, url])
            events_.append(event)
    return '\n'.join(events_)


def scrape_ticketmaster_attractions(attraction_id):
    print("Scraping attraction id = {}".format(attraction_id))
    link = TICKETMASTER_BASE_URL + TICKETMASTER_ATTRACTION_OBJECT + str(attraction_id[0]) + TICKETMASTER_JSON + \
          TICKETMASTER_SOURCE + TICKETMASTER_KEY
    response = requests.get(link)
    data = response.json()
    attraction_name = data['name']
    attraction_id = data['id']
    url = data['url']
    genre_obj = data['classifications'][0]['genre']
    genre_name = genre_obj['name']
    genre_id = genre_obj['id']
    attraction = ','.join([attraction_id, attraction_name, url, genre_id, genre_name])
    attractions_.append(attraction)
    return '\n'.join(attractions_)


def ticketmaster():
    dmas = get_ticketmaster_dmas()
    attraction_ids = get_ticketmaster_attraction_ids()
    close_database(connection)
    with Pool(10) as p:
        events = p.map(scrape_ticketmaster_events, dmas)
        attractions = p.map(scrape_ticketmaster_attractions, attraction_ids)
    with open("ticketmaster_events.txt", "w+") as file:
        file.write(''.join(events))
    file.close()
    with open("ticketmaster_attractions.txt", "w+") as file:
        file.write('\n'.join(attractions))
    file.close()


ticketmaster()
