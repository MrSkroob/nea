# testing for basic idea of adding blocks to a scratch project.
# this one is for a basic block.
import json
import zipfile
import re
import copy
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


TYPES = {
    "bool": "%b",
    "int": "%s",
    "str": "%s"
}


ARGUMENT_TYPES = {
    "bool": "argument_reporter_boolean",
    "int": "argument_reporter_string_number",
    "str": "argument_reporter_string_number"
}


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
    'inputs': {},
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


def load_python_file(file_name: str) -> list[str]:
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

    block_to_add = BLOCK_DATA.deepcopy()
    block_to_add["opcode"] = opcode_data["turn_right"]
    block_to_add["inputs"] = {"DEGREES": [1, [4, "15"]]}
    target_scripts[id] = block_to_add 
    

def save_data(file_name: str, data: dict):
    """Updates the json data inside the scratch project"""
    with zipfile.ZipFile("scratch_project/" + file_name, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as f:
        json_dumped = json.dumps(data, ensure_ascii=True)
        f.writestr("project.json", data=json_dumped)
        f.testzip()


def get_tokens(line: str):
    return [i.strip() for i in re.split(r'(\d+|\W+|\s+)', line) if i]


def get_variable_name(tokens: list[str]):
    tokens = [i.strip("\'\"[] ") for i in tokens]
    if "=" not in tokens: return -1
    return tokens.index("=") - 1


def get_variable_value(tokens: list[str]):
    index = tokens.index("=")
    if index == -1: return -1
    return index + 1


def get_value_in_brackets(line: str):
    re_object = re.search(BETWEEN_BRACKETS, line)
    param = re_object.group().replace(" ", "").split(",")
    return param


class Compiler():
    def __init__(self, file_to_compile: str, file_to_compile_to: str) -> None:
        self._target_code = load_python_file(file_to_compile)
        self._result_file_code = load_scratch_project(file_to_compile_to)

        self._compile_from = file_to_compile
        self._compile_to = file_to_compile_to

        self._sprite_list = [i["name"] for i in self._result_file_code["targets"]]
        self._block_dict = {}

        self._block_id = 0
        self._line_number = 0

    def generate_id(self):
        id_to_return = self._block_id
        self._block_id += 1
        return str(id_to_return) + "ID"

    def create_argument(self, argument_type: str, argument_name: str, parent: str):
        block_id = self.generate_id()
        argument_id = self.generate_id()

        # copy the template dictionary and apply the following attributes:
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = ARGUMENT_TYPES[argument_type]
        block_data_copy["shadow"] = True
        block_data_copy["topLevel"] = False
        block_data_copy["parent"] = parent
        block_data_copy["fields"] = {
            "VALUE": [
                argument_name,
                None
            ]
        }

        # adding the argument to its parent

        if self._block_dict[parent]["opcode"] == "procedures_prototype":
            self._block_dict[parent]["inputs"][argument_id] = [
                1,
                block_id
            ]

        # if it s a function (i.e. mutation), add the following properties to it:
        if "mutation" in self._block_dict[parent]:
            attributes = self._block_dict[parent]["mutation"]
            attributes["proccode"] += " " + TYPES[argument_type]
            attributes["argumentids"] = attributes["argumentids"][:-1] + '\"' + argument_id + '\",]'
            attributes["argumentnames"] = attributes["argumentnames"][:-1] + '\"' + argument_name + '\",]'
            attributes["argumentdefaults"] = attributes["argumentdefaults"][:-1] + '\"' + '\",]'

        # finally, add the actual block to the list to be saved to the scratch file
        self._block_dict[block_id] = block_data_copy
        return block_id

    
    def create_block(self, opcode: str, block_name: str, parent: str | None):
        block_id = self.generate_id()
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = opcode
        # things might get a lil' hard coded in here >:)
        if parent is not None:
            block_data_copy["topLevel"] = False
            if not parent in self._block_dict:
                raise ValueError("Parent does not exist!")
            block_data_copy["parent"] = parent
            if self._block_dict[parent]["opcode"] == "procedures_definition":
                pass
            else:
                self._block_dict[parent]["next"] = block_id
        
        if opcode == "procedures_prototype":
            # create the basic template for any future arguments to add. 
            block_data_copy["shadow"] = True
            block_data_copy["mutation"] = {
                "tagName": "mutation",
                "children": [],
                "proccode": block_name,
                "argumentids": "[]",
                "argumentnames": "[]",
                "argumentdefaults": "[]",
                "warp": True
            }
            self._block_dict[parent]["inputs"] = {
                "custom_block": [
                    1,
                    block_id
                ]
            }
        elif opcode == "":
            
            pass
        
        self._block_dict[block_id] = block_data_copy
        return block_id

    
    def compile(self):
        global_lists = {}
        global_variables = {} # store in studio
        local_lists = {}
        local_variables = {} # store in sprite

        studio_index = 0
        sprite_index = -1 # target index
        sprite_is_studio = False
        sprite_variable = ""

        for line_number, v in enumerate(self._target_code):
            # getting current sprite
            self._line_number = line_number
            indent_level = (len(v) - len(v.lstrip()))
            tokens = get_tokens(v)
            if sprite_variable == "":
                if "scratch_project.Sprite" in v:
                    # check if we've already defined a sprite variable
                    if sprite_variable: raise scratch_exceptions.TooManySprites

                    # check if sprite name is blank or not
                    re_object = re.search(BETWEEN_BRACKETS, v)
                    if re_object is None: raise scratch_exceptions.CouldNotFindSprite("")

                    # check if sprite actually exists
                    sprite_name = re_object.group().strip("\'\" ")
                    if sprite_name not in self._sprite_list: raise scratch_exceptions.CouldNotFindSprite(sprite_name)

                    index = get_variable_name(tokens)
                    sprite_variable = tokens[index]
                    sprite_index = self._sprite_list.index(sprite_name)

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
                    variable_id = self.generate_id()
                    if "[" in tokens[index + 1]:
                        # is a list!
                        if sprite_is_studio:
                            global_lists[variable_id] = [variable_name, []]
                        else:
                            local_lists[variable_id] = [variable_name, []]
                    else:
                        if sprite_is_studio: # if studio, we will make the variable global.
                            """
                            According to scratch wiki, global variables are stored in the stage. So this isn't a hack okay!!!!
                            """
                            global_variables[variable_id] = [variable_name, 0]
                        else:
                            local_variables[variable_id] = [variable_name, 0]
            elif "def" in tokens:
                function_name = tokens[tokens.index("def") + 2]
                function_parent_id = self.create_block("procedures_definition", "", None)

                function_id = self.create_block("procedures_prototype", function_name, function_parent_id)
                param_list = get_value_in_brackets(v)
                # creating the actual function block
                # self.create_block()

                if len(param_list) > 0 and param_list[0] != '':
                    for i in param_list:
                        split_param = i.split(":")
                        param = split_param[0]
                        param_type = split_param[1]

                        try:
                            TYPES[param_type]
                        except KeyError:
                            raise scratch_exceptions.InvalidArgumentType(param_type)
                        
                        # creating the actual input
                        self.create_argument(param_type, param, function_id)
                pass
                # ok let's try and creating a block
        pass

        # updating the project dictionary
        if not sprite_is_studio:
            # adding variables created in script
            for i in global_variables:
                self._result_file_code["targets"][studio_index]["variables"][i] = global_variables[i]

            for i in global_lists:
                self._result_file_code["targets"][studio_index]["lists"][i] = global_lists[i]

            for i in local_variables:
                self._result_file_code["targets"][sprite_index]["variables"][i] = local_variables[i]
            
            for i in local_lists:
                self._result_file_code["targets"][sprite_index]["lists"][i] = local_lists[i]
        
        self._result_file_code["targets"][sprite_index]["blocks"] = self._block_dict
        save_data(self._compile_to, self._result_file_code)


def main():
    # python_file_name = input("Python file to compile from: ")
    python_file_name = "scratch_example.py"

    # scratch_file_name = input("Scratch file to compile to: ")
    scratch_file_name = "Guinnea Pig.sb3"

    # opcode_data = get_block_opcode()
    compiler = Compiler(python_file_name, scratch_file_name)
    compiler.compile()
    # translate(python_code, scratch_file_name, project_json)
    

main()
