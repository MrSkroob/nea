# testing for basic idea of adding blocks to a scratch project.
# this one is for a basic block.
import json
import zipfile
import re
from dependencies import scratch_exceptions

# useful regexes
BETWEEN_BRACKETS = r"(?<=\()(.*?)(?=\))"
LEFT_VARIABLE_DEFINE = r"\w+\s?="

LEFT_OPERATOR_PLUS = r"\w+\s?\+"
LEFT_OPERATOR_MINUS = r"\w+\s?\-"
LEFT_OPERATOR_MUL = r"\w+\s?\*"
LEFT_OPERATOR_DIV = r"\w+\s?\/"

RIGHT_VARIABLE_DEFINE = r"=\s?\w+"
FUNCTION_NAME = r"(?<=def )(.*$)"
AFTER_COLON = r"(?<=:)(.*$)"

# scratch block scaffolding
KEYWORDS = [
    "if",
    "else",
    "def",
    "not",
    "or",
    "and",
    "True",
    "False"
]


BLOCK_DATA = {
    "opcode": "",
    "next": None, # next block, default None
    "parent": None, # previous block, default None
    "inputs": {},
    "fields": {},
    "shadow": False, # tells us whether the block is a "normal block" or a "shadow block. See definition above."
    "topLevel": True, # False if the block has a parent and true otherwise.
    "x": 0,
    "y": 0
}
PROCEDURE_DATA = { # this is the function call, hence the name.
    "opcode": "procedures_call",
    'next': None, 
    'parent': None, 
    'inputs': {
        "": [
            1,
            [
                10,
                "4"
            ]
        ]
    },
    "fields": {},
    "shadow": False,
    "x": 0,
    "y": 0
}
PROCEDURE_PROTOTYPE_DATA = { # this is the one that defines a procedure in Scratch.
    "opcode": "procedures_prototype",
    'next': None, 
    'parent': None, 
    'inputs': {},
    "fields": {},
    "shadow": False,
    "mutation": {
        "tagName": "mutation",
        "children": [], # this is normally empty anyway,
        "proccode": "", # procedure name
        "argumentids": "", # this is really cursed, it's an array within a string?
        "argumentdefaults": "", # same amount of curse-ness as argumentids
        "warp": False # tells scratch whether to run this with(out) screen refresh
    },
    "x": 0,
    "y": 0
}


def load_scratch_project(file_name: str) -> dict:
    """Returns the json data inside the scratch project with given file name"""
    with zipfile.ZipFile("scratch_project/" + file_name, "r") as f:
        project_json = json.loads(f.read("project.json").decode("utf-8"))
    return project_json


def load_python_file(file_name: str) -> dict:
    """Returns the contents of a text/python file"""
    with open(file_name, "r") as f:
        return f.readlines()


def get_block_opcode() -> dict:
    """Returns the dictionary of all attributes that a block has"""
    with open("dependencies/scratch_block_data.json") as f:
        json_file = json.load(f)
    return json_file


def add_block_example(project_json: dict, target_index: int, id: int, opcode_data: dict):
    """Adds a block to the project json"""
    """
    This is an example of how a block can be added to the json file.
    Right now, it creates a "turn right" block of 15 degrees and puts it 
    in the location 0, 0 (centre of the scratch editor)
    """
    target = project_json["targets"][target_index]
    target_scripts = target["blocks"]

    block_to_add = BLOCK_DATA.copy()
    block_to_add["opcode"] = opcode_data["turn_right"]
    block_to_add["inputs"] = {"DEGREES": [1, [4, "15"]]}
    target_scripts[id] = block_to_add 
    

def save_data(file_name: str, data: dict):
    """Updates the json data inside the scratch project"""
    with zipfile.ZipFile(file_name, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as f:
        json_dumped = json.dumps(data, ensure_ascii=False)
        f.writestr("project.json", data=json_dumped)
        f.testzip()


def get_tokens(line: str):
    return [i.strip() for i in re.split(r'(\d+|\W+)', line) if i]


def get_variable_name(tokens: list):
    tokens = [i.strip("\'\" ") for i in tokens]
    print(tokens)
    if "=" not in tokens: return -1
    return tokens.index("=") - 1


def get_variable_value(tokens: list):
    index = tokens.index("=")
    if index == -1: return -1
    return index + 1


def get_value_in_brackets(line: str):
    re_object = re.search(BETWEEN_BRACKETS, line)
    param = re_object.group().strip("\'\" ")
    params = param.split(",")
    return params


def translate(python_code: str, file_name: str, project_json: dict):
    id = 0 # id for each block

    sprite_list = [i["name"] for i in project_json["targets"]]
    indent_level = []

    global_variables = {} # store in studio
    local_variables = {} # store in sprite

    studio_index = 0
    sprite_index = -1 # target index
    sprite_is_studio = False
    sprite_variable = ""

    for i, v in enumerate(python_code):
        # getting current sprite
        indent_level.append(len(v) - len(v.lstrip()))
        tokens = get_tokens(v)
        if sprite_variable == "":
            if "scratch_project.Sprite" in v:
                if sprite_variable: raise scratch_exceptions.TooManySprites

                re_object = re.search(BETWEEN_BRACKETS, v)
                if re_object is None: raise scratch_exceptions.CouldNotFindSprite("")

                sprite_name = re_object.group().strip("\'\" ")
                if sprite_name not in sprite_list: raise scratch_exceptions.CouldNotFindSprite(sprite_name)
                index = get_variable_name(tokens)
                sprite_variable = tokens[index]
                sprite_index = sprite_list.index(sprite_name)
            elif "scratch_project.Studio" in v:
                if sprite_variable: raise scratch_exceptions.TooManySprites
                index = get_variable_name(tokens)
                sprite_variable = tokens[index]
                sprite_is_studio = True
                sprite_index = studio_index

        index = get_variable_name(tokens)
        if index != -1:
            variable_name = tokens[index]
            if variable_name != sprite_variable:
                if sprite_is_studio: # if studio, we will make the variable global.
                    """
                    According to scratch wiki, global variables are stored in the stage. So this isn't a hack okay!!!!
                    """
                    global_variables[variable_name] = [variable_name, 0]
                else:
                    local_variables[variable_name] = [variable_name, 0]
            
        elif "def" in tokens:
            pass
            # ok let's try and creating a block
    pass

    # updating the project dictionary
    if not sprite_is_studio:
        project_json["targets"][sprite_index]["variables"] = local_variables
        project_json["targets"][studio_index]["variables"] = global_variables
        print("====VARIABLES====")
        print("LOCAL", sprite_name , local_variables)
        print("GLOBAL", global_variables)

        print(project_json["targets"][sprite_index]["variables"])

    print(project_json)
    save_data(file_name, project_json)



def main():
    # python_file_name = input("Python file to compile from: ")
    python_file_name = "scratch_example.py"
    python_code = load_python_file(python_file_name)

    # scratch_file_name = input("Scratch file to compile to: ")
    scratch_file_name = "Empty Scratch Project.sb3"
    project_json = load_scratch_project(scratch_file_name)

    opcode_data = get_block_opcode()
    translate(python_code, scratch_file_name, project_json)
    

main()