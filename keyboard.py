import logging
from pynput.keyboard import Key, Controller as KeyboardController

class Keyboard:

    __keyboard_api: KeyboardController = None
    __pressed_keys: list[str] = None

    __key_overrides = {
        'space': Key.space,
        'ctrl_l': Key.ctrl_l,
        'tab': Key.tab,
        'shift_l': Key.shift_l
    }

    def __init__(self):
        self.__keyboard_api = KeyboardController()
        self.__pressed_keys = []

    def press(self, key: str):
        if self.is_pressed(key):
            logging.warning('Key is already pressed. Will not press again.')
        else:
            ko = self.__key_overrides.get(key, key)
            self.__keyboard_api.press(ko)
            self.__pressed_keys.append(key)


    def release(self, key: str):
        if self.is_pressed(key):
            ko = self.__key_overrides.get(key, key)
            self.__keyboard_api.release(ko)
            self.__pressed_keys.remove(key)
        else:
            logging.warning('Key is not pressed. Will not release.')

    def is_pressed(self, key: str):
        try:
            self.__pressed_keys.index(key)
            return True
        except ValueError:
            return False