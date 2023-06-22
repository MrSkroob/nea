import zipfile
import json
import re
import scratch_exceptions


IGNORE = [
    "from",
    "import"
]


BLOCK_DATA = {
    "opcode": "",
    "next": None,
    "parent": None,
    "inputs": {},
    "fields": {},
    "shadow": False,
    "topLevel": True,
    "x": 0,
    "y": 0
}


PROCEDURE_DATA = {
    "opcode": "procedures_call",
    'next': '', 
    'parent': None, 
    'inputs': {
        "custom_block": [
            1,
            "" # block_id
        ]
    },
    "fields": {},
    "shadow": False,
    "x": 0,
    "y": 0
}


PROCEDURE_PROTOTYPE_DATA = {
    "opcode": "procedures_prototype",
    'next': '', 
    'parent': '', 
    'inputs': {
        "" # id
    },
    "fields": {},
    "shadow": False,
    "mutation": {
        "tagName": "mutation",
        "children": [], # this is normally empty anyway,
        "proccode": "", # procedure name
        "argumentids": "", # this is really cursed, it's an array within a string?
        "argumentdefaults": "", # same amount of curse-ness as argumentids
        "warp": False
    },
    "x": 0,
    "y": 0
}


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


def contains_ignore(line: str):
    for i in IGNORE:
        if i in line:
            return True
    return False


def contains(line: str, item: str):
    return item in line


def get_block_data():
    with open("scratch_block_data.json") as f:
        json_file = json.load(f)
    return json_file


def load_project(file_name: str) -> json:
    with zipfile.ZipFile(file_name) as f:
        project_file = json.loads(f.read("project.json").decode("utf-8"))
    return project_file


def save_data(file_name: str, data):
    with zipfile.ZipFile(file_name, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as f:
        json_dumped = json.dumps(data, ensure_ascii=False)
        f.writestr("project.json", data=json_dumped)
        f.testzip()


def foo_bar(): # test function for adding a turn right block.
    project_json = load_project("Empty Scratch Project.sb3")
    blocks = project_json["targets"][1]["blocks"]
    block_data = BLOCK_DATA.copy()
    block_data["opcode"] = "motion_turnright"
    block_data["inputs"] = {"DEGREES": [1, [4, '15']]}

    # blocks[id]

    blocks["0"] = block_data

    save_data("Empty Scratch Project.sb3", project_json)


def compile(code: list, compile_to: str):
    # load_project(compile_to)
    block_id = 0
    input_id = 0
    parent = ""
    parent_variable_name = ""
    variables = []
    lists = []
    broadcasts = []
    custom_blocks = []
    compiled_result = {}
    for index in range(len(code)): # oh god i feel like im gonna commit sewerslide after this
        line = code[index]

        split = line.split(" ")
        no_whitespace = line.strip()

        if no_whitespace.find("from") != -1 or no_whitespace.find("import") != 1: 
            if contains(line, "scratch_project") != -1 or contains(line, "scratch_enums") != -1:
                continue
            else:
                raise scratch_exceptions.UnsupportedFeature("imports")
        elif not no_whitespace: 
            continue

        indents = len(line) - len(line.lstrip())

        if contains(line, ".Sprite("):
            if parent:
                raise scratch_exceptions.TooManySprites
            
            re_object = re.search(BETWEEN_BRACKETS, line)
            if re_object is None:
                raise scratch_exceptions.CouldNotFindSprite("")
            parent = re_object.group().strip().strip('"')
            if parent not in sprite_names:
                raise scratch_exceptions.CouldNotFindSprite(parent)

            parent_variable_name = line.split(" ")[0]

        if not parent: raise scratch_exceptions.MissingSpriteOrStudio
        if contains(line, "lambda"): raise scratch_exceptions.NoAnonymousProcedures
        if contains(line, "class"): raise scratch_exceptions.UnsupportedFeature("class")
        if contains(line, "return"): raise scratch_exceptions.NoReturn
        if contains(line, "{"): raise scratch_exceptions.UnsupportedFeature("dictionaries")
        if contains(line, "}"): raise scratch_exceptions.UnsupportedFeature("dictionaries")
        # if contains(line, "def "): # defined a function
        #     function_name_re = re.search(FUNCTION_NAME, line)
        #     if function_name_re is None:
        #         raise scratch_exceptions.NoAnonymousProcedures
            
        #     function_name = function_name_re.group()
        #     parameters_re = re.search(BETWEEN_BRACKETS, line)
        #     parameters = parameters_re.group()
        #     for i in parameters.split(", "):
        #         print(i)
        #         param_type_re = re.search(AFTER_COLON, i)
        #         if param_type_re is None:
        #             raise scratch_exceptions.MissingArgumentType
        #         param_type = param_type_re.group().strip()
        #         if param_type in ["int", "float"]:
        #             function_name += " %s"
        #         elif param_type == "bool":
        #             function_name += " %s"
        #         else:
        #             raise scratch_exceptions.InvalidArgumentType(param_type)

        #     function_block_data = json_data["def"]
        #     function_block_data["proccode"] = function_name
        #     compiled_result[str(block_id)] = json_data["def"]
        #     custom_blocks.append(function_name)
        #     try:
        #         func_index = index
        #         func_line = code[func_index + 1]

        #         func_indents = indents
        #         while func_indents != indents:
        #             func_indents = func_line[func_index]
        #             func_index += 1
        #             func_indents = len(func_line) - len(line.lstrip())
        #             block_id += 1
        #     except IndexError:
        #         pass

        elif contains(line, "="):
            variable_name_re = re.search(LEFT_VARIABLE_DEFINE, line)
            if variable_name_re:
                variable_name = variable_name_re.group()
                if variable_name in ["+", "-", "*", "/"]:
                    pass
                variables.append(variable_name)
                

        if contains(line, parent_variable_name + "."):
            block_name = ""
            pass

        block_id += 1

    raise NotImplementedError("Compiler reached here with no problems :)")
    # with zipfile.ZipFile(compile_to, "w") as f:
    #     json.dumps()


def load_python_file(file_name: str):
    with open(file_name, "r") as f:
        compile(f.readlines(), None)


if __name__ == "__main__":
    json_data = get_block_data()
    project_json = load_project("Scratch Project.sb3")
    sprite_names = []
    for i in project_json["targets"]:
        print(i)
        sprite_name = i["name"].strip('"')
        sprite_names.append(sprite_name)
    # foo_bar()
    # load_python_file("scratch_example.py")