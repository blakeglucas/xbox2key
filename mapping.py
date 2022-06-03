from typing import TextIO
from yaml import load, SafeLoader

class ButtonMapping(object):

    keycode: str
    toggle = False
    joy = False
    pos_keycode: str
    pos_thresh: float
    neg_keycode: str
    neg_thresh: float

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

class Mapping:

    __mappings: dict[str, ButtonMapping] = None

    def __init__(self, filelike: TextIO):
        self.__mappings = {}
        raw_mappings: dict = load(open(filelike, 'r'), SafeLoader)
        for k, v in raw_mappings.items():
            self.__mappings[k] = ButtonMapping(v)    

    def get_mapping(self, cmd) -> ButtonMapping | None:
        return self.__mappings.get(cmd, None)