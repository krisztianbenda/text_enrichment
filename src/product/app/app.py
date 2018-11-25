import requests
import simplejson as json
import wikipedia as wiki
from flask import Flask, request, render_template
from werkzeug.exceptions import abort

from document import Document, supported_entities, documents
from entity import EntityEncoder

app = Flask(__name__)

ner_endpoint = 'http://172.17.0.1:5001/text-processing/ner'
respond_handler = 'http://172.17.0.1:5000/text-enrichment/processed-entities'


@app.route('/text-enrichment/new-doc', methods=['POST'])
def add_document():
    if 'text' not in json.loads(request.data).keys():
        abort(400)
    doc = Document(request.data)
    documents[doc.id] = doc
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
                       'entities': json.dumps(documents[doc_id].entities, cls=EntityEncoder),
                       'text': documents[doc_id].text})


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
    return json.dumps({"labels": documents[doc_id].get_label_names()})


@app.route('/text-enrichment/<doc_id>/summary', methods=['GET'])
def get_summary(doc_id):
    if doc_id not in documents.keys():
        abort(404)

    labels = documents[doc_id].get_label_names()
    label_summary = []
    summary = {}
    for label in labels:
        summary[label] = []
        for entity in documents[doc_id].entities:
            if entity.label_name == label:
                label_summary.append({'expression': entity.expression,
                                      'start_char': entity.start_char,
                                      'end_char': entity.end_char,
                                      'link': entity.link})
        summary[label] = label_summary
        label_summary = []
    return json.dumps({"summary": summary, "labels": documents[doc_id].get_label_names()})


if __name__ == "__main__":
    wiki.set_lang('en')
    app.run(host='0.0.0.0', port=5000)
