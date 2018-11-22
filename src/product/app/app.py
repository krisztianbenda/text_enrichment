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
documents_dict = {}


class Document:

    text = str
    id = str
    data_id = str
    status = str

    def __init__(self, json_string):
        self.__dict__ = json.loads(json_string)
        self.id = gen_doc_id()
        self.data_id = str(uuid())
        self.status = 'initialized'
        documents_dict[self.id] = self


def gen_doc_id():
    new_id = randint(100000, 999999)
    while new_id in documents_dict.keys():
        randint(100000, 999999)
    return str(new_id)


@app.route('/', methods=['POST'])
def add_document():
    if 'text' not in json.loads(request.data).keys():
        abort(400)
    doc = Document(request.data)
    data[doc.data_id] = 'in progress'
    requests.post(ner_endpoint, json={'endpoint': respond_handler, 'id': doc.data_id, 'text': doc.text})
    return doc.id


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<doc_id>', methods=['GET'])
def get_results_page(doc_id):
    if doc_id not in documents_dict.keys():
        abort(404)
    return render_template('results.html')


@app.route('/api/<doc_id>', methods=['GET'])
def get_results(doc_id):
    if doc_id not in documents_dict.keys():
        abort(404)
    results = data[documents_dict[doc_id].data_id]
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
