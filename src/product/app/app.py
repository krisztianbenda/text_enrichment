import requests
from flask import Flask, request, render_template
import simplejson as json
from random import randint
from uuid import uuid4 as uuid
from datetime import timedelta
import dateutil.parser as time_parser
import unidecode
import sys

from werkzeug.exceptions import abort
import googlemaps
import wikipedia as wiki

app = Flask(__name__)

ner_endpoint = 'http://127.0.0.1:5001/text_enrichment/ner'
respond_handler = 'http://127.0.0.1:5000/text_enrichment/doc/entities'

documents_dict = {}
google_api_key = 'AIzaSyDHPFTie9AvvVFqXTCI5a43UBI8qkzLvXk'
gmaps = googlemaps.Client(key=google_api_key)
cse_engine_id = '005196073466017333319:sj3-tx-jmis'
wiki.set_lang('en')


def build_maps_link(place):
    # geocode_results = gmaps.geocode(place)
    # Erdetileg ez lenne a valasz a Mount Everestre:
    geocode_results = [{'address_components': [
        {'long_name': 'Mount Everest', 'short_name': 'Monte Everest', 'types': ['establishment', 'natural_feature']}],
        'formatted_address': 'Mt Everest',
        'geometry': {'location': {'lat': 27.9881206, 'lng': 86.9249751}, 'location_type': 'APPROXIMATE',
                     'viewport': {'northeast': {'lat': 27.9979732, 'lng': 86.94098249999999},
                                  'southwest': {'lat': 27.9782671, 'lng': 86.90896769999999}}},
        'place_id': 'ChIJvZ69FaJU6DkRsrqrBvjcdgU', 'plus_code': {'global_code': '7MV8XWQF+6X'},
        'types': ['establishment', 'natural_feature']}]
    print(geocode_results)
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
    return "https://www.google.hu/search?hl=en&q=" + unidecode.unidecode(expression).replace(' ', '+')


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


class Document:
    text = str
    id = str
    data_id = str
    status = str
    entities = [dict]

    def __init__(self, json_string):
        self.__dict__ = json.loads(json_string)
        self.id = gen_doc_id()
        self.data_id = str(uuid())
        self.status = 'initialized'
        documents_dict[self.id] = self

    def process_entities(self):
        entity_options = {'LOC': process_loc,
                          'GPE': process_gpe,
                          'EVENT': process_event,
                          'ORG': process_org,
                          'WORK_OF_ART': process_work_of_art,
                          'DATE': process_date,
                          'TIME': process_time,
                          'PERSON': process_person
                          }
        for entity in self.entities:
            for key in entity.keys():
                if entity[key] in entity_options.keys():
                    link = entity_options[entity[key]](key)
                    entity[key] = {'label': entity[key], 'link': link}
                else:
                    entity[key] = {'label': 'NOT_SUPPORTED', 'link': ""}


def gen_doc_id():
    new_id = randint(100000, 999999)
    while new_id in documents_dict.keys():
        randint(100000, 999999)
    return 'doc-' + str(new_id)


# /text_enrichment/doc/new_doc
@app.route('/', methods=['POST'])
def add_document():
    if 'text' not in json.loads(request.data).keys():
        abort(400)
    doc = Document(request.data)
    doc.status = 'in progress'
    print(doc.id)
    requests.post(ner_endpoint, json={'endpoint': respond_handler, 'id': doc.data_id, 'text': doc.text})
    return doc.id


@app.route('/text_enrichment', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/text_enrichment/<doc_id>', methods=['GET'])
def get_results_page(doc_id):
    if doc_id not in documents_dict.keys():
        abort(404)
    return render_template('results.html')


# /text_enrichment/doc/results/<doc_id>
@app.route('/api/<doc_id>', methods=['GET'])
def get_results(doc_id):
    if doc_id not in documents_dict.keys():
        abort(404)
    if documents_dict[doc_id].status == 'in progress':
        return json.dumps({'status': 'in progress'})
    return json.dumps({'status': 'ready', 'entities': json.dumps(documents_dict[doc_id].entities)})


@app.route('/text_enrichment/doc/entities', methods=['POST'])
def add_entities():
    r_data = json.loads(request.data)
    for doc in documents_dict.values():
        if doc.data_id == r_data['id']:
            print(r_data['entities'])
            doc.entities = r_data['entities']
            doc.process_entities()
            doc.status = 'done'
    return 'ok'


if __name__ == "__main__":
    app.run()
