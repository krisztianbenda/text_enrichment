from threading import Thread

import requests
from flask import Flask, request
import simplejson as json
import spacy


from werkzeug.exceptions import abort

app = Flask(__name__)

nlp = spacy.load("en_core_web_lg")


def do_NER(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append([ent.text, ent.label_, ent.start_char, ent.end_char])
    return entities


def process_request(data):
    ents = do_NER(data['text'])
    requests.post(data['endpoint'], json={'id': data['id'], 'entities': ents})


@app.route('/text_enrichment/ner', methods=['POST'])
def handle_request():
    data = json.loads(request.data)
    if 'text' not in data.keys() or 'id' not in data.keys() or 'endpoint' not in data.keys():
        abort(400)

    thread = Thread(target=process_request, kwargs={'data': data})
    thread.start()
    return 'started'


if __name__ == "__main__":
    app.run(port=5001)
