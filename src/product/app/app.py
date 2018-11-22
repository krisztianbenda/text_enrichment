import requests
from flask import Flask, request, render_template
import simplejson as json
from random import randint
from uuid import uuid4 as uuid

from werkzeug.exceptions import abort
import googlemaps
import wikipedia as wiki

app = Flask(__name__)

ner_endpoint = 'http://127.0.0.1:5001/text_enrichment/ner'
respond_handler = 'http://127.0.0.1:5000/text_enrichment/doc/entities'

documents_dict = {}
gmaps = googlemaps.Client(key='AIzaSyDHPFTie9AvvVFqXTCI5a43UBI8qkzLvXk')


def build_maps_link(place):
    # Tulleptem a napi limitet, 👇 ezert nem ad vissza eredmenyt
    # geocode_results = gmaps.geocode(location)
    # Erdetileg ez lenne a valasz a Mount Everestre:
    geocode_results = [{'address_components': [{'long_name': 'Mount Everest', 'short_name': 'Monte Everest', 'types': ['establishment', 'natural_feature']}], 'formatted_address': 'Mt Everest', 'geometry': {'location': {'lat': 27.9881206, 'lng': 86.9249751}, 'location_type': 'APPROXIMATE', 'viewport': {'northeast': {'lat': 27.9979732, 'lng': 86.94098249999999}, 'southwest': {'lat': 27.9782671, 'lng': 86.90896769999999}}}, 'place_id': 'ChIJvZ69FaJU6DkRsrqrBvjcdgU', 'plus_code': {'global_code': '7MV8XWQF+6X'}, 'types': ['establishment', 'natural_feature']}]
    # Ilyen linkke kell alakitani:
    # https://www.google.com/maps/search/?api=3&query=27.9881206,86.9249751&query_place_id=ChIJvZ69FaJU6DkRsrqrBvjcdgU
    return ('https://www.google.com/maps/search/?api=1&' +
            'query=' + str(geocode_results[0]['geometry']['location']['lat']) +
            ',' + str(geocode_results[0]['geometry']['location']['lng']) +
            '&query_place_id=' + str(geocode_results[0]['place_id']))


def build_wiki_link(entity):
    return wiki.set_lang('en').page(entity).url


def process_loc(location):
    return build_maps_link(location)


def process_gpe(gpe):
    return build_maps_link(gpe)


def process_org(org):
    return build_wiki_link(org)


def process_event(event):
    return build_wiki_link(event)


def process_woa(woa):
    print("CURRENTLY NOT SUPPORTED: " + woa)


def process_date(date):
    print("CURRENTLY NOT SUPPORTED: " + date)


def process_time(time):
    print("CURRENTLY NOT SUPPORTED: " + time)


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
                          'WORK_OF_ART': process_woa,
                          'DATE': process_date,
                          'TIME': process_time
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
    requests.post(ner_endpoint, json={'endpoint': respond_handler, 'id': doc.data_id, 'text': doc.text})
    return doc.id


@app.route('/text_enrichment', methods=['GET'])
def index():
    return render_template('index.html')


# /text_enrichment/<doc_id>
@app.route('/<doc_id>', methods=['GET'])
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
