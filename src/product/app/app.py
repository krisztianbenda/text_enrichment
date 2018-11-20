import requests
from flask import Flask, request, render_template
import simplejson as json
from random import randint
from uuid import uuid4 as uuid

from werkzeug.exceptions import abort

app = Flask(__name__)

ner_endpoint = 'http://127.0.0.1:5001/'
respond_handler = 'http://127.0.0.1:5000/entities'

data = {}
doc_ids = {}


def gen_doc_id():
    id = randint(100000, 999999)
    while id in doc_ids.keys():
        randint(100000, 999999)
    return str(id)


@app.route('/', methods=['POST'])
def add_document():
    doc = json.loads(request.data)
    if 'text' not in doc.keys():
        abort(400)
    doc_id = gen_doc_id()
    data_id = str(uuid())
    doc_ids[doc_id] = data_id
    data[data_id] = 'in progress'
    requests.post(ner_endpoint, json={'endpoint': respond_handler, 'id': data_id, 'text': doc['text']})
    return doc_id


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<doc_id>', methods=['GET'])
def get_results_page(doc_id):
    if doc_id not in doc_ids.keys():
        abort(404)
    return render_template('results.html')


@app.route('/api/<doc_id>', methods=['GET'])
def get_results(doc_id):
    if doc_id not in doc_ids.keys():
        abort(404)
    results = data[doc_ids[doc_id]]
    if results == 'in progress':
        return json.dumps({'status': 'in progress'})
    return json.dumps({'status': 'ready', 'entities': results})


@app.route('/entities', methods=['POST'])
def add_entities():
    r_data = json.loads(request.data)
    data[r_data['id']] = json.dumps({'entities': r_data['entities']})
    return 'ok'


if __name__ == "__main__":
    app.run()
