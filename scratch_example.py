from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite1")

hello = "Hello world"

def repeat(times: int):
    index = 0
    while index < times:
        index += 1
        sprite.say(index)
        sprite.wait(0.5)

repeat(40)