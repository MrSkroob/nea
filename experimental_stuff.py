# mini experiment area to see the ins and outs of a scratch project

# https://en.scratch-wiki.info/wiki/Scratch_File_Format
# just having this here - it's a cheatsheet of what format the sb3 file is in.

# https://pypi.org/project/sb3/ 
# link for the sb3 parser I found online
# OH GOD THERE IS NO DOCUMENTATION

# turns out there is indeed a use for this, to find all the opcodes of the blocks!

import sb3


project, files = sb3.open_sb3("Empty Scratch Project.sb3")


stages = []
sprites = []

for i in project.targets:
    if type(i) is sb3.Sprite:
        sprites.append(i)
    elif type(i) is sb3.Stage:
        stages.append(i) # honestly, this shouldn't even have more than 1 length


print(project.targets[1].block_info.blocks())


for i in sprites:
    print("\nTARGET_NAME:", i.name)
    scripts = i.block_info.scripts()
    for script in scripts:
        print("\nNEW SCRIPT")
        for block in script:
            print(block)
            # print(block.opcode)
            # for input in block.inputs:
            #     print(input)
            # for field in block.fields:
            #     print(field)


# in the example project 'Scratch Project.sb3' it suggests that the 'looks_say' block runs before the flagclicked event?
# It is consistantly placed above the event_whenflagclicked.


