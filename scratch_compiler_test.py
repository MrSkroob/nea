# testing for basic idea of adding blocks to a scratch project.
# this one is for a basic block.
import json
import zipfile
import re
import copy
from dependencies import scratch_exceptions

# useful regexes
BETWEEN_BRACKETS = r"(?<=\()(.*?)(?=\))"
LEFT_OPERATOR_EQUAL = r".+?(?=\=)"
LEFT_OPERATOR_PLUS = r".+?(?=\+=)"
LEFT_OPERATOR_MINUS = r".+?(?=\-=)"
LEFT_OPERATOR_MUL = r".+?(?=\*=)"
LEFT_OPERATOR_DIV = r".+?(?=\/=)"
LEFT_OPERATOR_MOD = r".+?(?=\%=)"

RIGHT_OPERATOR_EQUAL = r"(?<=\=).*"
RIGHT_OPERATOR_PLUS = r"(?<=\+=).*"
RIGHT_OPERATOR_MINUS = r"(?<=\-=).*"
RIGHT_OPERATOR_MUL = r"(?<=\*=).*"
RIGHT_OPERATOR_DIV = r"(?<=\/=).*"
RIGHT_OPERATOR_MOD = r"(?<=\%=).*"

GET_LEFT_SIDE = [
    LEFT_OPERATOR_PLUS,
    LEFT_OPERATOR_MINUS,
    LEFT_OPERATOR_MUL,
    LEFT_OPERATOR_DIV,
    LEFT_OPERATOR_MOD,
    LEFT_OPERATOR_EQUAL # this is ordered at the back so we check other operators first. 
                        # not doing this will make += match to =, resulting in the variable name being
                        # "variable_1 +"
]

GET_RIGHT_SIDE = [
    RIGHT_OPERATOR_PLUS,
    RIGHT_OPERATOR_MINUS,
    RIGHT_OPERATOR_MUL,
    RIGHT_OPERATOR_DIV,
    RIGHT_OPERATOR_MOD,
    RIGHT_OPERATOR_EQUAL
]

# regexes for operators without =
LEFT_COMPARE = r".+?(?=\==)"
LEFT_PLUS = r".+?(?=\+)"
LEFT_MINUS = r".+?(?=\-)"
LEFT_MUL = r".+?(?=\*)"
LEFT_DIV = r".+?(?=\/)"
LEFT_MOD = r".+?(?=\%)"

RIGHT_COMPARE = r"(?<=\==).*"
RIGHT_PLUS = r"(?<=\+).*"
RIGHT_MINUS = r"(?<=\-).*"
RIGHT_MUL = r"(?<=\*).*"
RIGHT_DIV = r"(?<=\/).*"
RIGHT_MOD = r"(?<=\%).*"

LEFT_OPERATOR = [
    LEFT_COMPARE,
    LEFT_PLUS,
    LEFT_MINUS,
    LEFT_MUL,
    LEFT_DIV,
    LEFT_MOD,
]

RIGHT_OPERATOR = [
    RIGHT_COMPARE,
    RIGHT_PLUS,
    RIGHT_MINUS,
    RIGHT_MUL,
    RIGHT_DIV,
    RIGHT_MOD,
]

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


OPERATORS = {
    "+=": "operator_add",
    "-=": "operator_subtract",
    "*=": "operator_multiply",
    "/=": "operator_divide",
    "%=": "operator_mod",

    "+": "operator_add",
    "-": "operator_subtract",
    "*": "operator_multiply",
    "/": "operator_divide",
    "%": "operator_mod",
}


OPERATOR_TYPE = {
    "+=": "+",
    "-=": "-",
    "*=": "*",
    "/=": "/",
    "%=": "%",

    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "%": "%",
    "=": "="
}

ARGUMENT_CODES = {
    str: "10",
    float: "4",
    int: "4"
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
    

def save_data(file_name: str, data: dict):
    """Updates the json data inside the scratch project"""
    with zipfile.ZipFile("scratch_project/" + file_name, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as f:
        json_dumped = json.dumps(data, ensure_ascii=True)
        f.writestr("project.json", data=json_dumped)
        f.testzip()


def get_tokens(line: str):
    return [i.strip() for i in re.split(r'(\d+|\W+|\s+)', line) if i]


def search(line: str, expression: str):
    match = re.search(expression, line)
    if match is not None:
        match = match.group().strip()
    return match


def get_variable_name(line: str):
    for i in GET_LEFT_SIDE:
        match = search(line, i)
        expression = i
        if match is not None: break
    return match, expression


def get_left_operator(line: str):
    for i in LEFT_OPERATOR:
        match = search(line, i)
        expression = i
        if match is not None: break
    return match, expression


def get_right_operator(line: str):
    for i in RIGHT_OPERATOR:
        match = search(line, i)
        expression = i
        if match is not None: break
    return match, expression

def get_operator(tokens: [str]):
    for i in OPERATOR_TYPE:
        if i in tokens:
            operator = i
            break
    return OPERATOR_TYPE[operator]


def get_variable_value(line: str):
    for i in GET_RIGHT_SIDE:
        match = search(line, i)
        expression = i
        if match is not None: break
    return match, expression


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
        self._existing_variables = {}
        self._block_dict = {}

        self._block_id = 0
        self._line_number = 0
        self._indent_level = 0

    def generate_id(self):
        """Generates a unique ID... by simply adding 1."""
        id_to_return = self._block_id
        self._block_id += 1
        return str(id_to_return) + "PY_TO_SCRATCH" # this mostly for debugging to tell me that it's generated by the compiler.

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
        del block_data_copy["x"]
        del block_data_copy["y"]

        # adding the argument to its parent

        if self._block_dict[parent]["opcode"] == "procedures_prototype":
            # if it is a function (i.e. mutation), add the following properties to it:            
            self._block_dict[parent]["inputs"][argument_id] = [
                1,
                block_id
            ]

            attributes = self._block_dict[parent]["mutation"]
            attributes["proccode"] += " " + TYPES[argument_type]
            if attributes["argumentids"] == "[]":
                # first time
                attributes["argumentids"] = attributes["argumentids"][:-1] + '\"' + argument_id + '\"]'
                attributes["argumentnames"] = attributes["argumentnames"][:-1] + '\"' + argument_name + '\"]'
                attributes["argumentdefaults"] = attributes["argumentdefaults"][:-1] + '\"' + '\"]'
            else:
                attributes["argumentids"] = attributes["argumentids"][:-1] + ',\"' + argument_id + '\"]'
                attributes["argumentnames"] = attributes["argumentnames"][:-1] + ',\"' + argument_name + '\"]'
                attributes["argumentdefaults"] = attributes["argumentdefaults"][:-1] + ',\"' + '\"]'


        # finally, add the actual block to the list to be saved to the scratch file
        self._block_dict[block_id] = block_data_copy
        return block_id
    
    def create_operator(self, opcode: str, values: list[dict, dict], parent: str | None):
        block_id = self.generate_id()
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = opcode

        if parent is not None:
            block_data_copy["parent"] = parent
            self._block_dict[parent]["inputs"]["VALUE"][1] = block_id


        if values[0]["VariableId"] is not None:
            value1_code = 3
            value1 = [
                12,
                values[0]["VariableName"],
                values[0]["VariableId"]
            ]
        else:
            value1_code = 1
            value1 = [
                4,
                values[0]["Value"]
            ]

        if values[1]["VariableId"] is not None:
            value2_code = 3
            value2 = [
                12,
                values[1]["VariableName"],
                values[1]["VariableId"]
            ]
        else:
            value2_code = 1
            value2 = [
                4,
                values[1]["Value"]
            ]

        block_data_copy["inputs"] = {
            "NUM1": [
                value1_code,
                value1,
                [
                    4,
                    ""
                ]
            ],
            "NUM2": [
                value2_code,
                value2,
                [
                    4,
                    ""
                ]
            ]
        }
        block_data_copy["topLevel"] = False

        del block_data_copy["x"]
        del block_data_copy["y"]

        self._block_dict[block_id] = block_data_copy
        return block_id
    
    def create_block(self, opcode: str, block_args: dict, parent: str | None):
        block_id = self.generate_id()
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = opcode
        # things might get a lil' hard coded in here >:)
        if parent is not None:
            block_data_copy["topLevel"] = False
            if not parent in self._block_dict:
                raise ValueError("Parent does not exist!")
            block_data_copy["parent"] = parent
            self._block_dict[parent]["next"] = block_id 
        if opcode != "procedures_prototype":
            block_data_copy["y"] = self._line_number * 25
        if opcode == "procedures_prototype":
            # create the basic template for any future arguments to add. 
            block_data_copy["shadow"] = True
            block_data_copy["mutation"] = {
                "tagName": "mutation",
                "children": [],
                "proccode": block_args["Name"],
                "argumentids": "[]",
                "argumentnames": "[]",
                "argumentdefaults": "[]",
                "warp": "false"
            }
            self._block_dict[parent]["inputs"] = {
                "custom_block": [
                    1,
                    block_id
                ]
            }
            del block_data_copy["x"]
            del block_data_copy["y"]
        elif opcode == "data_setvariableto":
            if block_args["OperatorId"] is not None:
                block_data_copy["inputs"]["VALUE"] = [
                    3,
                    block_args["OperatorId"],
                    [
                        10,
                        "0"
                    ]
                ]
            else:
                block_data_copy["inputs"]["VALUE"] = [
                        1,
                        [
                            10,
                            block_args["Value"]
                        ]
                    ]
            block_data_copy["fields"] = {
                "VARIABLE": [
                    block_args["Name"],
                    block_args["VariableId"]
                ]
            }
        elif opcode == "data_changevariableby":
            if block_args["ValueId"] is not None:
                block_data_copy["inputs"]["VALUE"] = [
                    3,
                    [
                        12,
                        block_args["ValueName"],
                        block_args["ValueId"]
                    ],
                    [
                        4,
                        "1"
                    ]
                ]
            else:
                block_data_copy["inputs"]["VALUE"] = [
                    1,
                    [
                        4,
                        block_args["Value"]
                    ]
                ]
            
            block_data_copy["fields"] = {
                "VARIABLE": [
                    block_args["Name"],
                    block_args["VariableId"]
                ]
            }

        self._block_dict[block_id] = block_data_copy
        return block_id
    
    # def create_set_value(self, variable_name: str, expression: str, operator: str, existing_variables: list, most_recent_block: list):
    #     if expression in existing_variables:
    #         if operator == "+":
    #             most_recent_block[self._indent_level] = self.create_block("data_changevariableby", {"Name": variable_name, "VariableId": existing_variables[variable_name], "ValueId": existing_variables[assigned_expression], "ValueName": assigned_expression}, most_recent_block[self._indent_level])
    #         else:
    #             most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": existing_variables[variable_name], "OperatorId": "TEMP"}, most_recent_block[self._indent_level])
    #             self.create_operator(OPERATORS[operator], [{"VariableName": variable_name, "VariableId": existing_variables[variable_name]}, {"VariableName": assigned_expression, "VariableId": existing_variables[assigned_expression]}], most_recent_block[self._indent_level])
    #     elif expression in function_parameters[self._indent_level]:
    #         if operator == "+":
    #             most_recent_block[self._indent_level] = self.create_block("data_changevariableby", {"Name": variable_name, "VariableId": function_parameters[self._indent_level][variable_name], "ValueId": function_parameters[self._indent_level][assigned_expression], "ValueName": assigned_expression}, most_recent_block[self._indent_level])
    #         else:
    #             most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": function_parameters[self._indent_level][variable_name], "OperatorId": "TEMP"}, most_recent_block[self._indent_level])
    #             self.create_operator(OPERATORS[operator], [{"VariableName": variable_name, "VariableId": function_parameters[self._indent_level][variable_name]}, {"VariableName": assigned_expression, "VariableId": function_parameters[self._indent_level][assigned_expression]}], most_recent_block[self._indent_level])
    #     else:
    #         most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": existing_variables[variable_name], "OperatorId": "TEMP"}, most_recent_block[self._indent_level])
    #         left_value, _ = get_left_operator(expression)
    #         right_value, _ = get_right_operator(expression)

    #         if left_value in existing_variables.keys():
    #             left_value = {"VariableName": left_value, "VariableId": existing_variables[left_value]}
    #         elif left_value in function_parameters[self._indent_level]:
    #             left_value = {"VariableName": left_value, "VariableId": function_parameters[self._indent_level][left_value]}
    #         else:
    #             left_value = {"VariableId": None, "Value": left_value}
    #         if right_value in existing_variables.keys():
    #             right_value = {"VariableName": right_value, "VariableId": existing_variables[right_value]}
    #         elif right_value in function_parameters[self._indent_level]:
    #             right_value = {"VariableName": right_value, "VariableId": function_parameters[self._indent_level][right_value]}
    #         else:
    #             right_value = {"VariableId": None, "Value": right_value}

    #         self.create_operator(OPERATORS[operator], [left_value, right_value], most_recent_block[self._indent_level])

    def compile(self):
        global_lists = {}
        global_variables = {} # store in studio
        local_lists = {}
        local_variables = {} # store in sprite

        function_parameters = {}
        existing_variables = {}

        studio_index = 0
        sprite_index = -1 # target index
        sprite_is_studio = False
        sprite_variable = ""

        most_recent_block = {0: self.create_block("event_whenflagclicked", {}, None)}

        for line_number, v in enumerate(self._target_code):
            # getting current sprite
            self._line_number = line_number
            self._indent_level = (len(v) - len(v.lstrip())) // 4

            if self._indent_level not in most_recent_block.keys():
                most_recent_block[self._indent_level] = None

            print(self._indent_level, most_recent_block[self._indent_level], line_number + 1)

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

                    sprite_variable, _ = get_variable_name(v)
                    sprite_index = self._sprite_list.index(sprite_name)
                    existing_variables[sprite_variable] = "PY_COMPILER"

                elif "scratch_project.Studio" in v:
                    if sprite_variable: raise scratch_exceptions.TooManySprites

                    sprite_variable, _ = get_variable_name(v)
                    sprite_is_studio = True
                    sprite_index = studio_index
                    existing_variables[sprite_variable] = "PY_COMPILER"

            variable_name, _ = get_variable_name(v)
            if variable_name is not None:
                if variable_name not in existing_variables.keys():
                    if variable_name != sprite_variable:
                        variable_value, _ = get_variable_value(v)
                        variable_id = self.generate_id()
                        if "[" in variable_value:
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
                            
                            most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "Value": str(variable_value), "VariableId": variable_id, "OperatorId": None}, most_recent_block[self._indent_level])
                        existing_variables[variable_name] = variable_id
                elif variable_name != sprite_variable:
                    operator = get_operator(tokens)
                    assigned_expression, _ = get_variable_value(v)
                    if assigned_expression in existing_variables:
                        if operator == "+":
                            most_recent_block[self._indent_level] = self.create_block("data_changevariableby", {"Name": variable_name, "VariableId": existing_variables[variable_name], "ValueId": existing_variables[assigned_expression], "ValueName": assigned_expression}, most_recent_block[self._indent_level])
                        else:
                            most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": existing_variables[variable_name], "OperatorId": "TEMP"}, most_recent_block[self._indent_level])
                            self.create_operator(OPERATORS[operator], [{"VariableName": variable_name, "VariableId": existing_variables[variable_name]}, {"VariableName": assigned_expression, "VariableId": existing_variables[assigned_expression]}], most_recent_block[self._indent_level])
                    elif assigned_expression in function_parameters[self._indent_level]:
                        if operator == "+":
                            most_recent_block[self._indent_level] = self.create_block("data_changevariableby", {"Name": variable_name, "VariableId": function_parameters[self._indent_level][variable_name], "ValueId": function_parameters[self._indent_level][assigned_expression], "ValueName": assigned_expression}, most_recent_block[self._indent_level])
                        else:
                            most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": function_parameters[self._indent_level][variable_name], "OperatorId": "TEMP"}, most_recent_block[self._indent_level])
                            self.create_operator(OPERATORS[operator], [{"VariableName": variable_name, "VariableId": function_parameters[self._indent_level][variable_name]}, {"VariableName": assigned_expression, "VariableId": function_parameters[self._indent_level][assigned_expression]}], most_recent_block[self._indent_level])
                    else:
                        most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": existing_variables[variable_name], "OperatorId": "TEMP"}, most_recent_block[self._indent_level])
                        left_value, _ = get_left_operator(assigned_expression)
                        right_value, _ = get_right_operator(assigned_expression)

                        if left_value in existing_variables.keys():
                            left_value = {"VariableName": left_value, "VariableId": existing_variables[left_value]}
                        elif left_value in function_parameters[self._indent_level]:
                            left_value = {"VariableName": left_value, "VariableId": function_parameters[self._indent_level][left_value]}
                        else:
                            left_value = {"VariableId": None, "Value": left_value}
                        if right_value in existing_variables.keys():
                            right_value = {"VariableName": right_value, "VariableId": existing_variables[right_value]}
                        elif right_value in function_parameters[self._indent_level]:
                            right_value = {"VariableName": right_value, "VariableId": function_parameters[self._indent_level][right_value]}
                        else:
                            right_value = {"VariableId": None, "Value": right_value}

                        self.create_operator(OPERATORS[operator], [left_value, right_value], most_recent_block[self._indent_level])
            elif "def" in tokens:
                function_name = tokens[tokens.index("def") + 2]
                print("FUNCTION DEFINITION ON LINE", line_number + 1)
                most_recent_block[self._indent_level + 1] = self.create_block("procedures_definition", {}, None)
                print("FUNCTION ID:", most_recent_block[self._indent_level + 1])
                function_id = self.create_block("procedures_prototype", {"Name": function_name}, most_recent_block[self._indent_level + 1])
                param_list = get_value_in_brackets(v)

                params = {}

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
                        argument_id = self.create_argument(param_type, param, function_id)
                        params[param] = argument_id
                        
                # creating list of params for this specific function so we can use it in variables later. 
                function_parameters[self._indent_level + 1] = params
        pass

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
