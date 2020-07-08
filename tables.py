from flask_table import Table, Col, DateCol
from flask_table.html import element


class URLCol(Col):
    def __init__(self, name, url_attr, **kwargs):
        self.url_attr = url_attr
        super(URLCol, self).__init__(name, **kwargs)

    def td_contents(self, item, attr_list):
        text = self.from_attr_list(item, attr_list)
        url = self.from_attr_list(item, [self.url_attr])
        return element('a', {'href': url}, content=text)


class MeetupTable(Table):
    th_html_attrs = {'data-show-header': 'false'}
    classes = ['table', 'table-sm', 'table-borderless']
    no_items = "Sorry, no relevant Meetup groups found"
    name = URLCol('', url_attr='group_url', attr='group_name')


class EventsTable(Table):
    classes = ['table', 'table-hover']
    thead_classes = ['thead-light']
    no_items = "Sorry, no events found"
    date = DateCol('Date')
    artist = URLCol('Artist', url_attr='artist_url', attr='artist')
    venue = URLCol('Venue', url_attr='venue_url', attr='venue')
    genre = Col('Genre')
    meetup = Col('Meetup Groups')

