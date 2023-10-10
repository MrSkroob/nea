# this script is for autocompletion for Scratch methods. 
# the compiler will use the exact names to know what block to create. 
# so far it doesn't do that because i haven't coded it in...

from __future__ import annotations
from . import scratch_enums

class Studio():
    """Note that most methods in here functionally don't do anything. They are used for the compiler"""
    def __init__(self) -> None:
        # internal, for compiler use
        self._project_path = ""

        # internal
        self._events = {}

        # looks
        self.backdrop_number = 0
        self.backdrop_name = 0

        # sound
        self.volume = 0

        # sensing
        self.answer = ""
        self.mouse_x = 0
        self.mouse_y = 0
        self.loudness = 0
        self.timer = 0
        self.current_year = 0
        self.current_month = 0
        self.current_date = ""
        self.current_day_of_week = ""
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.days_since_2000 = 0
        self.username = ""

    # internal
    def dictionary_to_edit(self, dictionary: dict):
        self._project_path = dictionary

    # events
    def when_key_pressed(self, keycode: scratch_enums.KeyCode, code: function):
        pass
    def when_backdrop_switches_to(self, backdrop: str, code: function):
        pass
    def when_exceeds(self, attribute: scratch_enums.AttributeEvent, value: int | float, code: function):
        pass
    def when_i_receive(self, message: str, code: function):
        pass

    def broadcast(self, message: str):
        pass

    def broadcast_and_wait(self, message: str):
        pass

    # control
    def wait(self, seconds: int | float):
        return {
            "opcode": "control_wait",
            "inputs": {
                "DURATION": [
                    seconds
                ]
            }
        }
    
    def wait_until(self, evaluation: bool):
        pass
    def stop(self, location: scratch_enums.Stop):
        pass
    def create_clone_of(self, sprite: Sprite):
        pass
    
    # sensing
    def ask_and_wait(self, question: str):
        self.answer = input(question)
    def key(self, keycode: scratch_enums.KeyCode):
        pass
    def mouse_down(self) -> bool:
        return True
    def reset_timer(self):
        pass
    
    # looks
    def switch_backdrop_to(self, backdrop: int | str):
        pass
    def next_backdrop(self):
        pass
    def change_effect(self, attribute: scratch_enums.Effect, value: int | float):
        pass
    def set_effect(self, attribute: scratch_enums.Effect):
        pass
    def clear_graphic_effects(self):
        pass



class Sprite(Studio):
    def __init__(self, name: str) -> None:
        super().__init__()
        # motion
        self.x_position = 0
        self.y_position = 0
        self.direction = 0

        # looks
        self.costume_number = 0
        self.costume_name = "Costume1"
        self.size = 0

        self._name = name

    # motion
    def move(self, steps: int | float):
        pass
    def turn_left(self, degrees: int | float):
        pass
    def turn_right(self, degrees: int | float):
        pass
    def go_to(self, position: scratch_enums.Position):
        pass
    def go_to_x_y(self, position: scratch_enums.Coordinates):
        pass
    def glide(self, duration: int, position: scratch_enums.Coordinates):
        pass
    def point_in_direction(self, direction: int | float):
        self.direction = direction
        pass
    def point_towards(self, position: scratch_enums.Position.MOUSE_POINTER | Sprite):
        pass
    def change_x_by(self, x: int | float):
        pass
    def set_x_to(self, x: int | float):
        pass
    def change_y_by(self, y: int | float):
        pass
    def set_y_to(self, y: int | float):
        pass
    def if_on_edge_bounce(self):
        pass
    def set_rotation_style(self, rotation_style: scratch_enums.RotationStyle):
        pass

    # looks
    def say_for(self, message: str, duration: int | float):
        pass
    def say(self, message: str):
        pass
    def think_for(self, message: str, duration: int | float):
        pass
    def think(self, message: str):
        pass
    def switch_costume_to(self, costume: int | str):
        pass
    def next_costume(self):
        pass
    def change_size_by(self, size: int | float):
        pass
    def set_size_to(self, size: int | float):
        pass
    def show(self):
        pass
    def hide(self):
        pass
    def go_to_layer(self, layer: scratch_enums.Layer):
        pass
    def go_n_layers(self, layer_direction: scratch_enums.LayerDirection):
        pass

    # events
    def when_sprite_clicked(self, code: function):
        pass

    # control
    def delete_this_clone(self):
        pass
    def when_i_start_as_clone(self, code: function):
        pass
    