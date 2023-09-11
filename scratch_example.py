from dependencies import scratch_project, scratch_enums
# import scratch_compiler

sprite = scratch_project.Sprite("Sprite1")

variable_1 = 2
variable_2 = 4
boolean = (variable_1 + variable_2) * 8 + 4 * 3

if (boolean == 1) and not 2 == 1 or 8 == 2:
    variable_sam = "yay"
elif not 1 == 1:
    variable_sam = "nay"

def david_is_stinky(a: int, b: int):
    a += b

for i in range(20):
    pass