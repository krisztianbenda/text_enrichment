from uuid import uuid4 as uuid
import label

import simplejson as json
from unidecode import unidecode

from entity import Entity
from random import randint

supported_entities = ['LOC', 'GPE', 'EVENT', 'ORG', 'WORK_OF_ART', 'DATE', 'TIME', 'PERSON']
documents = {}


def gen_doc_id():
    new_id = randint(100000, 999999)
    while new_id in documents.keys():
        randint(100000, 999999)
    return 'doc-' + str(new_id)


class Document:
    text: str
    id: str
    data_id: str
    status: str
    entities: [Entity]
    required_labels: [str]

    def __init__(self, json_string):
        self.__dict__ = json.loads(json_string)
        self.id = gen_doc_id()
        self.data_id = str(uuid())
        self.status = 'initialized'
        self.entities = []
        self.required_labels = []
        input_json = json.loads(json_string)
        if 'required_labels' in input_json:
            for label in input_json['required_labels']:
                self.required_labels.append(label)
        else:
            '''Don't process labels'''

    def process_entities(self, entities):
        entity_options = {'LOC': label.LocLabel,
                          'GPE': label.GpeLabel,
                          'EVENT': label.EventLabel,
                          'ORG': label.OrgLabel,
                          'WORK_OF_ART': label.WordOfArtLabel,
                          'DATE': label.DateLabel,
                          'TIME': label.TimeLabel,
                          'PERSON': label.PersonLabel
                          }
        for entity in entities:
            if len(entity) != 4:
                print('There is a problem with the entity fields length: {}'.format(entity))
                continue
            if entity[1] in entity_options.keys() and entity[1] in self.required_labels:
                label_obj = entity_options[entity[1]](entity[0])
                link = label_obj.process_label()
                new_entity: Entity = Entity(unidecode(entity[0]), entity[1], entity[2], entity[3], link)
                self.entities.append(new_entity)
            else:
                '''Found entity not supported'''
                print('Found entity not supported or not required: {} - {}'.format(entity[0], entity[1]))

    def get_label_names(self) -> [str]:
        labels = []
        for entity in self.entities:
            if entity.label_name not in labels:
                labels.append(entity.label_name)
        labels.sort()
        return labels

