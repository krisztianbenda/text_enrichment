import requests
from flask import Flask, request, render_template
import simplejson as json
from random import randint
from uuid import uuid4 as uuid
from datetime import timedelta
import dateutil.parser as time_parser
import unidecode

from werkzeug.exceptions import abort
import googlemaps
import wikipedia as wiki

app = Flask(__name__)

ner_endpoint = 'http://127.0.0.1:5001/text_enrichment/ner'
respond_handler = 'http://127.0.0.1:5000/text_enrichment/doc/entities'

documents = {}
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
    # print(geocode_results)
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


class Entity(object):
    expression: str
    label: str
    link: str
    start_char: int
    end_char: int

    def __init__(self, expression, label, start_char, end_char, link):
        self.expression = expression
        self.label = label
        self.link = link
        self.start_char = start_char
        self.end_char = end_char


class EntityEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Entity):
            return o.__dict__
        return EntityEncoder(self, o)


class Document:
    text: str
    id: str
    data_id: str
    status: str
    entities: [Entity]

    def __init__(self, json_string):
        self.__dict__ = json.loads(json_string)
        self.id = gen_doc_id()
        self.data_id = str(uuid())
        self.status = 'initialized'
        self.entities = []
        documents[self.id] = self

    def process_entities(self, entities):
        entity_options = {'LOC': process_loc,
                          'GPE': process_gpe,
                          'EVENT': process_event,
                          'ORG': process_org,
                          'WORK_OF_ART': process_work_of_art,
                          'DATE': process_date,
                          'TIME': process_time,
                          'PERSON': process_person
                          }
        for entity in entities:
            if len(entity) != 4:
                print('There is a problem with the entity fields length: {}'.format(entity))
                continue
            if entity[1] in entity_options.keys():
                link = entity_options[entity[1]](entity[0])
                new_entity: Entity = Entity(unidecode.unidecode(entity[0]), entity[1], entity[2], entity[3], link)
                self.entities.append(new_entity)
            else:
                '''Found entity not supported'''
                print('Found entity not supported: {} - {}'.format(entity[0], entity[1]))

    def get_labels(self):
        labels = []
        for entity in self.entities:
            if entity.label not in labels:
                labels.append(entity.label)
        labels.sort()
        return labels


def gen_doc_id():
    new_id = randint(100000, 999999)
    while new_id in documents.keys():
        randint(100000, 999999)
    return 'doc-' + str(new_id)


# /text_enrichment/new_doc ❌
@app.route('/', methods=['POST'])
def add_document():
    if 'text' not in json.loads(request.data).keys():
        abort(400)
    doc = Document(request.data)
    doc.status = 'in progress'
    requests.post(ner_endpoint, json={'endpoint': respond_handler, 'id': doc.data_id, 'text': doc.text})
    return doc.id


# /text_enrichment ✅
@app.route('/text_enrichment', methods=['GET'])
def index():
    return render_template('index.html')


# /text_enrichment/<doc_id> ✅
@app.route('/text_enrichment/<doc_id>', methods=['GET'])
def get_results_page(doc_id):
    if doc_id not in documents.keys():
        abort(404)
    return render_template('results.html')


# /text_enrichment/<doc_id>/results ❌
@app.route('/api/<doc_id>', methods=['GET'])
def get_results(doc_id):
    if doc_id not in documents.keys():
        abort(404)
    if documents[doc_id].status == 'in progress':
        return json.dumps({'status': 'in progress'})
    return json.dumps({'status': documents[doc_id].status,
                       'entities': json.dumps(documents[doc_id].entities, cls=EntityEncoder)})


# /text_enrichment/upload_entities ❌
@app.route('/text_enrichment/doc/entities', methods=['POST'])
def add_entities():
    r_data = json.loads(request.data)
    for doc in documents.values():
        if doc.data_id == r_data['id']:
            doc.process_entities(r_data['entities'])
            doc.status = 'processed'
    return 'ok'


# /text_enrichment/<doc_id>/labels ✅
@app.route('/text_enrichment/<doc_id>/labels', methods=['GET'])
def get_labels(doc_id):
    if doc_id not in documents.keys():
        abort(404)
    return json.dumps({"labels": documents[doc_id].get_labels()})


@app.route('/text_enrichment/<doc_id>/summary', methods=['GET'])
def get_summary(doc_id):
    if doc_id not in documents.keys():
        abort(404)

    labels = documents[doc_id].get_labels()
    label_summary = []
    summary = {}
    for label in labels:
        summary[label] = []
        for entity in documents[doc_id].entities:
            if entity.label == label:
                label_summary.append({'expression': entity.expression,
                                      'start_char': entity.start_char,
                                      'end_char': entity.end_char,
                                      'link': entity.link})
        summary[label] = label_summary
        label_summary = []
    return json.dumps(summary)



if __name__ == "__main__":
    app.run()
