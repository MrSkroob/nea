import json
from dependencies.project_loading_utils import load_project


project_json = load_project("scratch_project/Empty Scratch Project.sb3")


# print(json.dumps(project_json, indent=4))
# print("\n")


for i in project_json["targets"]:
    print("\nTARGET:", i["name"])
    print(i["variables"])
    blocks = i["blocks"]
    for id in blocks:
        print(id, json.dumps(blocks[id], indent=4))


# example of block data:
# for "motion_turnleft":
# "DEGREES" : [ -- obviously the name of the parameter
#   1 -- See below
#   [ 
#       4, -- See below
#       "15" -- This is the value inputed by the user, i.e. 15 degrees
#   ]
# ]

"""
From: https://en.scratch-wiki.info/wiki/Scratch_File_Format

A shadow block is a reporter in an input for which one can enter or pick a value, 
and which cannnot be dragged around but can be replaced by a normal reporter.
[7] Scratch internally considers these to be blocks although they are not usually thought of as such. 
(These notions come from Blockly, which Scratch Blocks is based on.) 

An object associating names with arrays representing inputs into which other blocks may be dropped, including C mouths. 
The first element of each array is 1 if the input is a shadow, 2 if there is no shadow, and 3 if there is a shadow but it is obscured by the input.

The second is either the ID of the input or an array representing it as described in the table below. 
If there is an obscured shadow, the third element is its ID or an array representing it.
"""