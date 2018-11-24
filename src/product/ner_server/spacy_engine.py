import spacy

possible_models = ['en_core_web_sm', 'en_core_web_md', 'en_core_web_lg']


class NEREngine:
    def __init__(self, model):
        if model in possible_models:
            self.model_name = model
        else:
            '''Invalid model passed to the engine'''
            self.model_name = 'en_core_web_lg'
        self.nlp = spacy.load(self.model_name)

    def process_text(self, text):
        doc = self.nlp(text)
        entities = []
        for entity in doc.ents:
            entities.append([entity.text, entity.label_, entity.start_char, entity.end_char])
        return entities
