from uuid import uuid4 as uuid

import simplejson as json
from unidecode import unidecode

from entity import Entity
from label import process_loc, process_gpe, process_event, process_org, process_work_of_art, process_date, \
    process_time, process_person


class Document:
    text: str
    id: str
    data_id: str
    status: str
    entities: [Entity]

    def __init__(self, json_string, doc_id):
        self.__dict__ = json.loads(json_string)
        self.id = doc_id
        self.data_id = str(uuid())
        self.status = 'initialized'
        self.entities = []

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
                new_entity: Entity = Entity(unidecode(entity[0]), entity[1], entity[2], entity[3], link)
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
