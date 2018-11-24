import argparse
from threading import Thread
import requests
import simplejson as json
from flask import Flask, request
from werkzeug.exceptions import abort
import spacy_engine

parser = argparse.ArgumentParser(prog='NER Engine Server',
                                 description="Welcome to the NER Engine's Server! You can specify a SpaCy NER model "
                                             "through the model argument. For more information about the models see: "
                                             "https://spacy.io/models/#available-models")
parser.add_argument('-m', '--model', type=str, default='en_core_web_lg',
                    help="Say which model you want to use. en_core_web_sm, en_core_web_md and en_core_web_lg are "
                         "supported")
parser.add_argument('-p', '--port', type=int, default=5001,
                    help="Specify the used port by the NER Engine server. Default is 5001")

app = Flask(__name__)
engine = None


def process_request(data):
    entities = engine.process_text(data['text'])
    requests.post(data['endpoint'], json={'id': data['id'], 'entities': entities})


@app.route('/text_enrichment/ner', methods=['POST'])
def handle_request():
    data = json.loads(request.data)
    if 'text' not in data.keys() or 'id' not in data.keys() or 'endpoint' not in data.keys():
        abort(400)

    thread = Thread(target=process_request, kwargs={'data': data})
    thread.start()
    return 'processing is started...'


def initialize_model(spacy_model):
    global engine
    engine = spacy_engine.NEREngine(spacy_model)


if __name__ == "__main__":
    args = parser.parse_args()
    model_name = args.model
    initialize_model(model_name)
    app.run(port=args.port)
