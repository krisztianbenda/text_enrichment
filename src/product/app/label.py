from datetime import timedelta

import dateutil.parser as time_parser
import wikipedia as wiki
from unidecode import unidecode
import googlemaps

# To use Google Maps we need to provide a Google API key.
# If API key not provided, the program will use the Mount Everest as default location to every LOC and GPE
google_api_key = 'XXXX-XXXX-XXXX-XXXX'
gmaps = googlemaps.Client(key=google_api_key)


class Label:
    expression: str

    def __init__(self, name):
        self.expression = name

    def build_search_link(self):
        return "https://www.google.hu/search?hl=en&q=" + unidecode(self.expression).replace(' ', '+')

    def build_wiki_link(self):
        try:
            return wiki.page(self.expression).url
        except wiki.exceptions.PageError:
            return self.build_search_link()

    def build_maps_link(self):
        if google_api_key != '':
            geocode_results = gmaps.geocode(self.expression)
        else:
            geocode_results = [{'address_components': [
                {'long_name': 'Mount Everest', 'short_name': 'Monte Everest',
                 'types': ['establishment', 'natural_feature']}],
                'formatted_address': 'Mt Everest',
                'geometry': {'location': {'lat': 27.9881206, 'lng': 86.9249751}, 'location_type': 'APPROXIMATE',
                             'viewport': {'northeast': {'lat': 27.9979732, 'lng': 86.94098249999999},
                                          'southwest': {'lat': 27.9782671, 'lng': 86.90896769999999}}},
                'place_id': 'ChIJvZ69FaJU6DkRsrqrBvjcdgU', 'plus_code': {'global_code': '7MV8XWQF+6X'},
                'types': ['establishment', 'natural_feature']}]
        if len(geocode_results) == 0:
            '''Location Not Found => we just search for it on Google'''
            return self.build_wiki_link()
        return ('https://www.google.com/maps/search/?api=1&' +
                'query=' + str(geocode_results[0]['geometry']['location']['lat']) +
                ',' + str(geocode_results[0]['geometry']['location']['lng']) +
                '&query_place_id=' + str(geocode_results[0]['place_id']))

    def build_calendar_link(self):
        # noinspection PyBroadException
        try:
            date = time_parser.parse(self.expression)
            return ('https://www.google.com/calendar/render?action=TEMPLATE&' +
                    'text=' + 'Event+From+Text+Enrichment' +
                    '&dates=' + date.strftime('%Y%m%dT%H%M%SZ') + '/' + (date + timedelta(hours=1)).strftime(
                        '%Y%m%dT%H%M%SZ') +
                    '&details=' + 'This+date+and+time+found+by+text+enrichment'
                    # + '&location=' + 'Waldorf+Astoria,+301+Park+Ave+,+New+York,+NY+10022&sf=true&output=xml'
                    )
        except ValueError as err:
            print(err)
            return 'NOT_SUPPORTED'

    def build_image_search_link(self):
        return "https://www.google.hu/search?hl=en&tbm=isch&q=" + self.expression.replace(' ', '+')

    def process_label(self):
        return self.build_search_link()


class GpeLabel(Label):
    def process_label(self):
        return self.build_maps_link()


class LocLabel(Label):
    def process_label(self):
        return self.build_maps_link()


class OrgLabel(Label):
    def process_label(self):
        return self.build_wiki_link()


class EventLabel(Label):
    def process_label(self):
        return self.build_wiki_link()


class WordOfArtLabel(Label):
    def process_label(self):
        return self.build_image_search_link()


class DateLabel(Label):
    def process_label(self):
        link = self.build_calendar_link()
        return link if link != 'NOT_SUPPORTED' else "Format is currently not supported"


class TimeLabel(Label):
    def process_label(self):
        link = self.build_calendar_link()
        return link if link != 'NOT_SUPPORTED' else "Format is currently not supported"


class PersonLabel(Label):
    def process_label(self):
        return self.build_wiki_link()
