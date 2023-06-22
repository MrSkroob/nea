from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite1")


hello = ""
another_variable = ""


def add(a, b):
    my_variable = a + b
    sprite.say(my_variable)

def green_flag_clicked():
    add(4, 8)    


sprite.green_flag_clicked(green_flag_clicked)
