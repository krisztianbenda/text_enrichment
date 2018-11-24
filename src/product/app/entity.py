import simplejson as json


class Entity(object):
    expression: str
    label: str
    link: str
    start_char: int
    end_char: int

    def __init__(self, expression, label, start_char, end_char, link):
        self.expression = expression
        self.label = label
        self.link = link
        self.start_char = start_char
        self.end_char = end_char


class EntityEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Entity):
            return o.__dict__
        return EntityEncoder(self, o)
