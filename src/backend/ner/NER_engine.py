import spacy


def do_NER(text):
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(text)
    ents = []
    for ent in doc.ents:
        ents.append([ent.text, ent.label_])
    return ents

