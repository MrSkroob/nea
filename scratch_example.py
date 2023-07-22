from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite1")

def add(a: int, b: int):
    my_variable = a + b
    sprite.say(my_variable)

