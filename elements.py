class Event(object):
    def __init__(self, date, artist, artist_url, venue, venue_url, genre, meetup_groups):
        self.date = date
        self.artist = artist
        self.artist_url = artist_url
        self.venue = venue
        self.venue_url = venue_url
        self.genre = genre
        self.meetup = meetup_groups


class MeetupGroup(object):
    def __init__(self, group_name, group_url):
        self.group_name = group_name
        self.group_url = group_url