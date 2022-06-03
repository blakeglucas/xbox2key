import argparse
from keyboard import Keyboard
from mapping import Mapping
from pyee.base import EventEmitter
from threading import Thread
import time
from xinput import XInput, XINPUT_GAMEPAD, XINPUT_BUTTONS, XINPUT_STATE

class ControllerMonitor(Thread):

    __xinputref = None
    __state = None

    def __init__(self, emitter: EventEmitter, ctrl_index = 0):
        super().__init__(daemon=True)
        self.__emitter = emitter
        self.__xinputref = XInput()
        self.ctrl_index = ctrl_index
        self.__state = self.get_controller_state()

    def run(self):
        while True:
            new_state = self.get_controller_state()
            new_state_set = set(new_state.items())
            cur_state_set = set(self.__state.items())
            diff_set = new_state_set ^ cur_state_set
            if len(diff_set) > 0:
                for k, v in diff_set:
                    if self.__state[k] != v:
                        self.__emitter.emit('state_change', k, v)
                self.__state = new_state
                # time.sleep(1)

    def get_controller_state(self):
        raw_state = self.__xinputref.GetState(self.ctrl_index)
        return self.__class__.xiapi_to_state(raw_state)

    @staticmethod
    def xiapi_to_state(state: tuple):
        '''
        Destructure all structs returned from XInput ABI
        '''
        gamepad: XINPUT_GAMEPAD = state[1]
        buttons: XINPUT_BUTTONS = gamepad.wButtons
        l_trigger = gamepad.bLeftTrigger
        r_trigger = gamepad.bRightTrigger
        l_joy_x = gamepad.sThumbLX
        l_joy_y = gamepad.sThumbLY
        r_joy_x = gamepad.sThumbRX
        r_joy_y = gamepad.sThumbRY
        dpad_up = buttons.DPAD_UP
        dpad_down = buttons.DPAD_DOWN
        dpad_left = buttons.DPAD_LEFT
        dpad_right = buttons.DPAD_RIGHT
        start = buttons.START
        back = buttons.BACK
        l_joy = buttons.LEFT_THUMB
        r_joy = buttons.RIGHT_THUMB
        l_bump = buttons.LEFT_SHOULDER
        r_bump = buttons.RIGHT_SHOULDER
        a = buttons.A
        b = buttons.B
        x = buttons.X
        y = buttons.Y
        r1 = buttons._reserved_1_
        r2 = buttons._reserved_2_
        local_vars = locals()
        return dict([(key, local_vars[key]) for key in ('l_trigger','r_trigger','l_joy_x', 'l_joy_y', 'r_joy_x', 'r_joy_y', 'dpad_up', 'dpad_down', 'dpad_left', 'dpad_right', 'start', 'back', 'l_joy', 'r_joy', 'l_bump', 'r_bump', 'a', 'b', 'x', 'y', 'r1', 'r2', )])

_buttons: Mapping = None
_keyboard: Keyboard = None

def _state_handler(xkey: str, new_value):
    global _buttons, _keyboard
    if _buttons is None:
        return None

    joy_pos_max = int((2**16 / 2))
    joy_neg_max = int(-1 * (2**16 / 2))

    assert (joy_pos_max - joy_neg_max) == 2**16, 'Invalid joy max values'

    btn_mapping = _buttons.get_mapping(xkey)
    if btn_mapping is None:
        return
    if btn_mapping.joy:
        pkc, pthr, nkc, nthr = (btn_mapping.pos_keycode, btn_mapping.pos_thresh, btn_mapping.neg_keycode, btn_mapping.neg_thresh)
        if new_value >= pthr * joy_pos_max:
            if not _keyboard.is_pressed(pkc):
                _keyboard.press(pkc)
        elif _keyboard.is_pressed(pkc):
            _keyboard.release(pkc)
        if new_value <= nthr * joy_neg_max:
            if not _keyboard.is_pressed(nkc):
                _keyboard.press(nkc)
        elif _keyboard.is_pressed(nkc):
            _keyboard.release(nkc)
        return
    key, toggle = (btn_mapping.keycode, btn_mapping.toggle)
    if toggle:
        if new_value == 0:
            return
        if _keyboard.is_pressed(key):
            _keyboard.release(key)
        else:
            _keyboard.press(key)
    else:
        if new_value == 1 or (xkey.endswith('_trigger') and new_value == 255):
            _keyboard.press(key)
        else:
            _keyboard.release(key)
    
def main():
    global _buttons, _keyboard
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapping', '-m', type=str, help='File containing Xbox controller to keyboard mappings in YAML')
    args = parser.parse_args()
    _buttons = Mapping(args.mapping)
    _keyboard = Keyboard()
    events = EventEmitter()
    events.on('state_change', _state_handler)
    ctrl_mon_thread = ControllerMonitor(events, ctrl_index=0)
    ctrl_mon_thread.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()