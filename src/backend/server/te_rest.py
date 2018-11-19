import uuid
from src.NER_engine import do_NER

texts = {str: uuid.UUID}


def post(input_text):
    text = input_text.get("text", None)

    if text in texts.keys():
        return texts[text]

    new_id = uuid.uuid1()
    texts[text] = new_id

    return do_NER(text)


