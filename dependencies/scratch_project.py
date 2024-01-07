# this script is for autocompletion for Scratch methods. 
# the compiler will use the exact names to know what block to create. 

from __future__ import annotations
from . import scratch_enums

class Studio():
    """Note that most methods in here functionally don't do anything. They are used for the compiler"""
    def __init__(self) -> None:
        # looks
        self.backdrop_number = 0
        self.backdrop_name = ""

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

    # events
    def when_key_pressed(self, keycode: scratch_enums.KeyCode, code: function = None):
        pass
    def when_backdrop_switches_to(self, backdrop: str, code: function = None):
        pass
    def when_exceeds(self, attribute: scratch_enums.AttributeEvent, value: int | float, code: function = None):
        pass
    def when_i_receive(self, message: str, code: function = None):
        pass

    def broadcast(self, message: str = None):
        pass

    def broadcast_and_wait(self, message: str = None):
        pass

    # control
    def wait(self, seconds: int | float = None):
        return {
            "opcode": "control_wait",
            "default": 5,
            "INPUT_DIR": ["DURATION"],
        }
    
    def wait_until(self, evaluation: bool = None):
        pass
    def stop(self, location: scratch_enums.Stop = None):
        pass
    def create_clone_of(self, sprite: Sprite = None):
        pass
    
    # sensing
    def ask_and_wait(self, question: str = None):
        self.answer = input(question)
    def key(self, keycode: scratch_enums.KeyCode = None):
        pass
    def mouse_down(self) -> bool:
        return True
    def reset_timer(self):
        pass
    
    # looks
    def switch_backdrop_to(self, backdrop: int | str = None):
        pass
    def next_backdrop(self):
        pass
    def change_effect(self, attribute: scratch_enums.Effect, value: int | float = None):
        pass
    def set_effect(self, attribute: scratch_enums.Effect, value: int | float):
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
    def move(self, steps: int | float = None):
        pass
    def turn_left(self, degrees: int | float = None):
        pass
    def turn_right(self, degrees: int | float = None):
        pass
    def go_to(self, position: scratch_enums.Position = None):
        pass
    def go_to_x_y(self, position: scratch_enums.Coordinates = None):
        pass
    def glide(self, duration: int | float, position: scratch_enums.Coordinates = None):
        pass
    def point_in_direction(self, direction: int | float = None):
        self.direction = direction
        pass
    def point_towards(self, position: scratch_enums.Position.MOUSE_POINTER | Sprite = None):
        pass
    def change_x_by(self, x: int | float = None):
        pass
    def set_x_to(self, x: int | float = None):
        pass
    def change_y_by(self, y: int | float = None):
        pass
    def set_y_to(self, y: int | float = None):
        pass
    def if_on_edge_bounce(self):
        pass
    def set_rotation_style(self, rotation_style: scratch_enums.RotationStyle = None):
        pass

    # looks
    def say_for(self, message: str, duration: int | float = None):
        pass
    def say(self, message: str = None):
        return {
            "opcode": "looks_say",
            "default": 10,
            "INPUT_DIR": ["MESSAGE"]
        }
    def think_for(self, message: str, duration: int | float = None):
        pass
    def think(self, message: str = None):
        pass
    def switch_costume_to(self, costume: int | str = None):
        pass
    def next_costume(self):
        pass
    def change_size_by(self, size: int | float = None):
        pass
    def set_size_to(self, size: int | float = None):
        pass
    def show(self):
        pass
    def hide(self):
        pass
    def go_to_layer(self, layer: scratch_enums.Layer = None):
        pass
    def go_n_layers(self, layer_direction: scratch_enums.LayerDirection = None):
        pass

    # events
    def when_sprite_clicked(self, code: function = None):
        pass

    # control
    def delete_this_clone(self):
        pass
    def when_i_start_as_clone(self, code: function = None):
        pass
    