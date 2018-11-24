from random import randint

import googlemaps
import requests
import simplejson as json
import wikipedia as wiki
from flask import Flask, request, render_template
from werkzeug.exceptions import abort

from document import Document, supported_entities
from entity import EntityEncoder

app = Flask(__name__)

ner_endpoint = 'http://127.0.0.1:5001/text-processing/ner'
respond_handler = 'http://127.0.0.1:5000/text-enrichment/processed-entities'

documents = {}
google_api_key = 'AIzaSyDHPFTie9AvvVFqXTCI5a43UBI8qkzLvXk'
gmaps = googlemaps.Client(key=google_api_key)
cse_engine_id = '005196073466017333319:sj3-tx-jmis'
wiki.set_lang('en')


def gen_doc_id():
    new_id = randint(100000, 999999)
    while new_id in documents.keys():
        randint(100000, 999999)
    return 'doc-' + str(new_id)


@app.route('/text-enrichment/new-doc', methods=['POST'])
def add_document():
    if 'text' not in json.loads(request.data).keys():
        abort(400)
    doc_id = gen_doc_id()
    doc = Document(request.data, doc_id)
    documents[doc_id] = doc
    doc.status = 'in progress'
    requests.post(ner_endpoint, json={'endpoint': respond_handler, 'id': doc.data_id, 'text': doc.text})
    return doc.id


@app.route('/text-enrichment', methods=['GET'])
def index():
    return render_template('index.html', supported_entities=supported_entities)


@app.route('/text-enrichment/<doc_id>', methods=['GET'])
def get_results_page(doc_id):
    if doc_id not in documents.keys():
        abort(404)
    return render_template('results.html')


@app.route('/text-enrichment/<doc_id>/results', methods=['GET'])
def get_results(doc_id):
    if doc_id not in documents.keys():
        abort(404)
    if documents[doc_id].status == 'in progress':
        return json.dumps({'status': 'in progress'})
    return json.dumps({'status': documents[doc_id].status,
                       'entities': json.dumps(documents[doc_id].entities, cls=EntityEncoder)})


@app.route('/text-enrichment/processed-entities', methods=['POST'])
def add_entities():
    r_data = json.loads(request.data)
    for doc in documents.values():
        if doc.data_id == r_data['id']:
            doc.process_entities(r_data['entities'])
            doc.status = 'processed'
    return 'ok'


@app.route('/text-enrichment/<doc_id>/labels', methods=['GET'])
def get_labels(doc_id):
    if doc_id not in documents.keys():
        abort(404)
    return json.dumps({"labels": documents[doc_id].get_labels()})


@app.route('/text-enrichment/<doc_id>/summary', methods=['GET'])
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
