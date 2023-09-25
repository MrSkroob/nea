from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite1")

finished = 8 + 2

var = 8
finished = var

for i in range(4):
    var += 1
    if var == True:
        var = False
finished = True

def hello_world(value: str):
    finished = value

hello_world("wowzers")