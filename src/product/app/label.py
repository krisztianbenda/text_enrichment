from datetime import timedelta

import dateutil.parser as time_parser
import wikipedia as wiki
from unidecode import unidecode
import googlemaps


google_api_key = 'AIzaSyDHPFTie9AvvVFqXTCI5a43UBI8qkzLvXk'
gmaps = googlemaps.Client(key=google_api_key)


def build_maps_link(place):
    geocode_results = gmaps.geocode(place)
    # Erdetileg ez lenne a valasz a Mount Everestre:
    # geocode_results = [{'address_components': [
    #     {'long_name': 'Mount Everest', 'short_name': 'Monte Everest', 'types': ['establishment', 'natural_feature']}],
    #     'formatted_address': 'Mt Everest',
    #     'geometry': {'location': {'lat': 27.9881206, 'lng': 86.9249751}, 'location_type': 'APPROXIMATE',
    #                  'viewport': {'northeast': {'lat': 27.9979732, 'lng': 86.94098249999999},
    #                               'southwest': {'lat': 27.9782671, 'lng': 86.90896769999999}}},
    #     'place_id': 'ChIJvZ69FaJU6DkRsrqrBvjcdgU', 'plus_code': {'global_code': '7MV8XWQF+6X'},
    #     'types': ['establishment', 'natural_feature']}]
    if len(geocode_results) == 0:
        '''Location Not Found => we just search for it on Google'''
        return build_wiki_link(place)
    return ('https://www.google.com/maps/search/?api=1&' +
            'query=' + str(geocode_results[0]['geometry']['location']['lat']) +
            ',' + str(geocode_results[0]['geometry']['location']['lng']) +
            '&query_place_id=' + str(geocode_results[0]['place_id']))


def build_calendar_link(datetime_string):
    # noinspection PyBroadException
    try:
        date = time_parser.parse(datetime_string)
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


def build_wiki_link(entity):
    try:
        return wiki.page(entity).url
    except:
        return build_search_link(entity)


def build_image_search_link(expression):
    return "https://www.google.hu/search?hl=en&tbm=isch&q=" + expression.replace(' ', '+')


def build_search_link(expression):
    return "https://www.google.hu/search?hl=en&q=" + unidecode(expression).replace(' ', '+')


def process_loc(location):
    return build_maps_link(location)


def process_gpe(gpe):
    return build_maps_link(gpe)


def process_org(org):
    return build_wiki_link(org)


def process_event(event):
    return build_wiki_link(event)


def process_work_of_art(woa):
    return build_image_search_link(woa)


def process_date(date):
    link = build_calendar_link(date)
    return link if link != 'NOT_SUPPORTED' else "Format is currently not supported"


def process_time(time):
    link = build_calendar_link(time)
    return link if link != 'NOT_SUPPORTED' else "Format is currently not supported"


def process_person(person):
    return build_wiki_link(person)
