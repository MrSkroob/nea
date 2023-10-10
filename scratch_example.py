from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite2")

hello = "Hello world"
hello[2] = "!"

def repeat(times: int):
    index = 0
    while index < times:
        index += 1

repeat(40)