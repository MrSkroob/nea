# testing for basic idea of adding blocks to a scratch project.
# this one is for a basic block.
import time
import json
import zipfile
import re
import copy
from dependencies import scratch_exceptions
from dependencies.scratch_compiler_regex_utils import *

# useful regexes
SINGLE_EQUAL = r"(?<!=)=(?!=)"

TYPES = {
    "bool": "%b",
    "int": "%s",
    "str": "%s"
}


OPERATOR_LIST = [
    "operator_add",
    "operator_divide",
    "operator_subtract",
    "operator_multiply",
    "operator_mod",
]


BOOLEAN_OPERATOR_LIST = [
    "operator_equals",
    "operator_lt",
    "operator_gt",
    "operator_not",
    "operator_and",
    "operator_or"
]


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

STR_OPERATORS = {
    "+=": "operator_length",
    "+": "operator_length"
}

BOOLEAN_OPERATORS = {
    "。": "。", # I'll need special behaviour for this BECAUSE OF COURSE I DO
    "`": "operator_equals",
    "<": "operator_lt",
    ">": "operator_gt",
    "¬": "operator_not",
    "&": "operator_and",
    "|": "operator_or"
}


BOOLEAN_SUB = {
    "!=": "。",
    "==": "`",
    "<": "<",
    ">": ">",
    "not": "¬",
    "and": "&",
    "or": "|"
}


BOOLEAN_ORDER = [
    "(",
    "`",
    "¬",
    "<",
    ">",
    "¬",
    "&",
    "|"
]

# operators that combine 2 operators together
COMBINED_OPERATORS = {
    "+=": "+",
    "-=": "-",
    "*=": "*",
    "/=": "/",
    "%=": "%",
    "//=": "//"
    # "**=": "**" scratch doesn't natively have indices multiplication yet
}

# bodmas order
ORDER = [
    # highest precedence, lowest bottom
    "=",
    "-",
    "+",
    "//",
    "/",
    "*",
    "(",
]


REVERSED_ORDER = [
    "(",
    "*",
    "/",
    "//",
    "+",
    "-",
    "="
]


ARGUMENT_TYPES = {
    "bool": "argument_reporter_boolean",
    "int": "argument_reporter_string_number",
    "str": "argument_reporter_string_number"
}

# scratch block scaffolding
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
    

def save_data(file_name: str, data: dict):
    """Updates the json data inside the scratch project"""
    with zipfile.ZipFile("scratch_project/" + file_name, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as f:
        json_dumped = json.dumps(data, ensure_ascii=True)
        f.writestr("project.json", data=json_dumped)
        f.testzip()


class Compiler():
    def __init__(self, file_to_compile: str, file_to_compile_to: str) -> None:
        self._target_code = load_python_file(file_to_compile)
        self._result_file_code = load_scratch_project(file_to_compile_to)

        self._compile_from = file_to_compile
        self._compile_to = file_to_compile_to

        self._sprite_list = [i["name"] for i in self._result_file_code["targets"]]
        self._most_recent_if = {}
        self._function_variables = {}
        self._functions = {}
        self._generated_variables: dict[str: str] = {}
        self._generated_lists = {}
        self._most_recent_block = {}
        self._block_dict = {}

        self._block_id = 0
        self._temp_id = 0
        self._line_number = 0
        self._prev_line_number = -1
        self._if_layers = 0
        self._indent_level = 0

    def is_id(self, id: str):
        """Checks if the given string is a PY_TO_SCRATCH id."""
        if type(id) is not str:
            return False
        return id.find("PY_TO_SCRATCH") != -1

    def is_parameter(self, param_name: str):
        try:
            return param_name in self._function_variables[self._indent_level]
        except KeyError:
            return False

    def is_variable_id(self, id: str) -> tuple[bool, str | None]:
        for i in self._generated_variables:
            if self._generated_variables[i] == id:
                return True, i
        return False, None

    def replace_variable_name_with_id(self, line: str):
        # FIXME check if line is an actual string, so it doesn't get replaced with an id.
        if type(line) is not str:
            Warning("Expected a string, got type:", type(line))
            return line
        for i in self._generated_variables:
            line = re.sub(r"\b" + i + r"\b", self._generated_variables[i], line)
        return line

    def get_next_id(self):
        """Predicts what the next id might be"""
        return str(self._block_id + 1) + "PY_TO_SCRATCH"
    
    def generate_temp_id(self):
        """Generates a unique ID for future use"""
        self._temp_id += 1
        return str(self._temp_id - 1) + "PY_TO_SCRATCH"

    def generate_id(self):
        """Generates a unique ID... by simply adding 1."""
        id_to_return = self.get_next_id()
        self._block_id += 1
        self._temp_id = self._block_id
        return id_to_return # this mostly for debugging to tell me that it's generated by the compiler.

    def create_argument(self, argument_type: str, argument_name: str, parent: str, ID=None):
        """Creates an argument using the given parameters
        generally this is used for procedures only"""
        if ID is None:
            block_id = self.generate_id()
        else:
            block_id = ID
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
    
    def format_value_for_operator(self, value: dict, parent_id: str):
        """Formats the given value into something that can be read by Scratch in the table
        within an operator"""
        if value.get("VariableId", None) is not None:
            # checks if the first value is a variable
            value1 = [
                3,
                [
                    12,
                    value["VariableName"],
                    value["VariableId"]
                ]
            ]
        else:
            is_argument =  self.is_parameter(value["Value"])
            if self.is_id(value["Value"]):
                # check if value exists as an argument in a function
                success, name = self.is_variable_id(value["Value"])
                if is_argument or not success:
                    # this should always be true honestly
                    if is_argument:
                        root = self._function_variables[self._indent_level][value["Value"]]
                        param_type = root[1]
                        param = root[2]
                        value["Value"] = self.create_argument(param_type, param, parent_id)
                        self._block_dict[value["Value"]]["shadow"] = False
                    value1 = [
                        3,
                        value["Value"],
                        [
                            4,
                            ""
                        ]
                    ]
                else:
                    # variable
                    value1 = [
                        3,
                        [
                            12,
                            name,
                            value["Value"]
                        ],
                    ]
            else:
                value1 = [
                    1,
                    [
                        4,
                        value["Value"]
                    ]
                ]
        return value1

    def assign_to_default_operator(self, operator_to_assign_to: str, block_id: str):
        """Assigns value to numerical operator"""
        self.__assign_to_operator(operator_to_assign_to, block_id, "NUM")
    
    def assign_to_boolean_operator(self, operator_to_assign_to: str, block_id: str):
        """Assigns value to boolean operator"""
        self.__assign_to_operator(operator_to_assign_to, block_id, "OPERAND")
    
    def __assign_to_operator(self, operator_to_assign_to: str, block_id: str, parameter: str):
        """This should not be used outside of the two wrapper methods:
        assign_to_default_operator 
        and
        assign_to_boolean_operator"""
        param1 = parameter + "1"
        param2 = parameter + "2"
        if self._block_dict[operator_to_assign_to]["inputs"][param1][1] == block_id:
                self._block_dict[operator_to_assign_to]["inputs"][param1] = [
                    3,
                    block_id,
                    [
                        4,
                        ""
                    ]
                ]
        elif self._block_dict[operator_to_assign_to]["inputs"][param2][1] == block_id:
            self._block_dict[operator_to_assign_to]["inputs"][param2] = [
                3,
                block_id,
                [
                    4,
                    ""
                ]
            ]

    def operator_parent_to(self, block_data_copy: dict, child: str, parent: str):
        """Similar to the parent_to method, but is usable outside of its wrapper functions"""
        block_data_copy["parent"] = parent
        if self._block_dict[parent]["opcode"] == "control_if":
            self._block_dict[parent]["inputs"]["CONDITION"][1] = child
        elif self._block_dict[parent]["opcode"] == "operator_not":
            self._block_dict[parent]["inputs"]["OPERAND"] = [
                2,
                child
            ]
        elif self._block_dict[parent]["opcode"] == "control_repeat":
            self._block_dict[parent]["inputs"]["TIMES"] = [
                3,
                child,
                [
                    6,
                    "10"
                ]
            ]
        elif self._block_dict[parent]["opcode"] == "operator_length":
            value = self.format_value_for_operator(child, parent)
            self._block_dict[parent]["inputs"]["STRING"] = value
        elif self._block_dict[parent]["opcode"] in BOOLEAN_OPERATOR_LIST:
            # check if operator is a boolean operator
            self.assign_to_boolean_operator(parent, child)
        else:
            # operator is NOT a boolean operator
            try:
                # find the value variable inside
                self._block_dict[parent]["inputs"]["VALUE"][1] = child
            except KeyError:
                self.assign_to_default_operator(parent, child)

    def create_operator(self, opcode: str, values: list[dict, dict], parent: str | None, ID=None):
        """Creates an operator block given the parameters"""
        if ID is None:
            block_id = self.generate_id()
        else:
            block_id = ID
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = opcode

        self._block_dict[block_id] = block_data_copy

        if self._line_number not in self._function_variables.keys():
            self._function_variables[self._line_number] = []
        if parent is not None:
            self.operator_parent_to(block_data_copy, block_id, parent)
        value1 = self.format_value_for_operator(values[0], block_id)
        value2 = self.format_value_for_operator(values[1], block_id)
        if opcode in OPERATOR_LIST:
            block_data_copy["inputs"] = {
                "NUM1": value1,
                "NUM2": value2
            }
        elif opcode == "operator_not":
            # special behaviour for not gate as it only has one parameter
            # if the two values have different values we are SCREWED
            block_data_copy["inputs"]["OPERAND"] = [
                value1
            ]
        elif opcode == "operator_length":
            block_data_copy["inputs"]["STRING"] = value1
        else:
            block_data_copy["inputs"] = {
                "OPERAND1": value1,
                "OPERAND2": value2
            }
        block_data_copy["topLevel"] = False

        del block_data_copy["x"]
        del block_data_copy["y"]

        return block_id

    def __parent_to(self, block_data_copy: dict, block_args: dict, child: str, parent: str):
        """Parents the given block to its parent, should not be used outside of .create_block"""
        block_data_copy["topLevel"] = False
        parent_block = self._block_dict[parent]
        block_data_copy["parent"] = parent

        next_indent = self._most_recent_block.get(self._indent_level + 1, None)
        previous_indent = self._most_recent_block.get(self._indent_level - 1, None)

        if parent_block["opcode"] == "control_if":
            if previous_indent == parent or next_indent is None: 
                # this means that we are parenting inside of the substack
                parent_block["inputs"]["SUBSTACK"][1] = child
            else:
                # parent to outside the substack
                block_data_copy["parent"] = self._most_recent_if[self._indent_level]
                self._block_dict[self._most_recent_if[self._indent_level]]["next"] = child
        elif parent_block["opcode"] == "control_if_else":
            if block_args.get("PARENT_TO_ELIF", None) is not None:
                parent_block["inputs"]["SUBSTACK2"][1] = child
            elif previous_indent == parent or next_indent is None:
                # this means that we are parenting inside of the substack
                if parent_block["inputs"]["SUBSTACK2"][1] == "TEMP":
                    parent_block["inputs"]["SUBSTACK2"][1] = child
                else:
                    parent_block["next"] = child
            else:
                # parent to outside the substack
                # parent_block["next"] = child
                block_data_copy["parent"] = self._most_recent_if[self._indent_level]
                self._block_dict[self._most_recent_if[self._indent_level]]["next"] = child
        elif parent_block["opcode"] == "control_repeat":
            if previous_indent == parent or next_indent is None:
                parent_block["inputs"]["SUBSTACK"] =  [
                    2,
                    child
                ]
            else:
                parent_block["next"] = child
        else:
            self._if_layers = self._indent_level
            parent_block["next"] = child
 
    def create_block(self, opcode: str, block_args: dict, parent: str | bool, id_to_use=None):
        """Creates a block in a format that Scratch can read"""
        if id_to_use is None:
            block_id = self.generate_id()
        else:
            block_id = id_to_use
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = opcode
        if parent is None:
            parent = self._most_recent_block[self._indent_level - 1]
        if parent is not False:
            self.__parent_to(block_data_copy, block_args, block_id, parent)
        if opcode != "procedures_prototype":
            block_data_copy["y"] = self._line_number * 25
        else:
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
            # del block_data_copy["x"]
            # del block_data_copy["y"]
        if opcode == "procedures_call":
            block_data_copy = copy.deepcopy(self._block_dict[block_args["FunctionId"]])
            block_data_copy["opcode"] = opcode
            block_data_copy["shadow"] = False
            index = 0 
            for id in block_data_copy["inputs"]:
                if index >= len(block_args["Args"]): break
                if self.is_id(block_args["Args"][index]):
                    # is some sort of id.
                    success, variable_name = self.is_variable_id(block_args["Args"][index])
                    if success:
                        # argument is a variable!!!!
                        value = {"VariableName": variable_name, "VariableId": block_args["Args"][index]}
                        block_data_copy["inputs"][id] = [
                            3,
                            [
                                12,
                                value["VariableName"],
                                value["VariableId"]
                            ]
                        ]
                    else:
                        # should be an operator or a parameter of some sort of function
                        # if not... idk, panic? raise ScratchExceptions.Panic() :/
                        block_data_copy["inputs"][id] = [
                            3,
                            block_args["Args"][index],
                            [
                                10,
                                ""
                            ]
                        ]
                else:
                    block_data_copy["inputs"][id] = [
                        1,
                        [
                            10,
                            block_args["Args"][index]
                        ]
                    ]
                index += 1
            
            del block_data_copy["mutation"]["argumentnames"]
            del block_data_copy["mutation"]["argumentdefaults"]
        elif opcode == "data_setvariableto":
            if block_args.get("OperatorId", None) is not None:
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
                    block_args.get("VariableId", None)
                ]
            }
        elif opcode == "data_changevariableby":
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
                    block_args.get("VariableId", None)
                ]
            }
            pass
            # if block_args.get("value")
        elif opcode == "control_if":
            if block_args.get("CONDITION", None) is not None:
                block_data_copy["inputs"]["CONDITION"] = block_args["CONDITION"]
                block_data_copy["inputs"]["SUBSTACK"] = [2, "TEMP"]
        elif opcode == "control_repeat":
            if block_args.get("SUBSTACK", None) is not None:
                block_data_copy["inputs"]["SUBSTACK"] = block_args["SUBSTACK"]
            if block_args.get("TIMES", None) is not None:
                block_data_copy["inputs"]["TIMES"] = block_args["TIMES"]
            else:
                block_data_copy["inputs"]["TIMES"] = [
                    1,
                    [
                        6,
                        "10"
                    ]
                ]

        self._block_dict[block_id] = block_data_copy
        return block_id

    def create_variable_add_block(self, line: str, variable_id: str, data_block_type: str, parent: str):
        """Wrapper function:
        Creates a data_setvariableto block using the generate_evaluation method
        and automatically parents"""
        # we ignore anything before the = sign, because it's irrelevant
    
        root_operator, success = self.generate_evaluation(line)
        variable_name = self.get_variable_name_from_id(variable_id)
        opcode = "data_" + data_block_type
        if success is False:
            _, index = self.get_operator(root_operator, ORDER)
            right = root_operator[index + 1:]
            value = self.get_variable_table_for_operator(right)
            if value.get("VariableName", None) is not None:
                self._most_recent_block[self._indent_level] = self.create_block(opcode, {"Name": variable_name, "VariableId": variable_id, "OperatorId": value["VariableId"]}, parent)
            elif self.is_parameter(value["Value"]):
                value["Name"] = variable_name
                # we check if the "value" is part of the function parameter
                root = self._function_variables[self._indent_level][value["Value"]]
                # pre-generate id
                id_to_use = self.generate_id()
                value["Value"] = id_to_use
                value["OperatorId"] = id_to_use
                self._most_recent_block[self._indent_level] = self.create_block(opcode, value, parent)
                
                # because of the way I coded this, we have to parent the argument after creating the block. 
                # makes sense though, you can't have children if the parent doesn't exist.
                argument_id = self.create_argument(root[1], root[2], self._most_recent_block[self._indent_level], id_to_use)
                self._block_dict[argument_id]["shadow"] = False
            else:
                # regular value like 8 :P
                value["Name"] = variable_name
                self._most_recent_block[self._indent_level] = self.create_block(opcode, value, parent)
        else:
            self._most_recent_block[self._indent_level] = self.create_block(opcode, {"Name": variable_name, "VariableId": variable_id, "OperatorId": "TEMP"}, parent)
            self.operator_parent_to(self._block_dict[root_operator], root_operator, self._most_recent_block[self._indent_level])

    def get_variable_table_for_operator(self, potential_variable_name: str):
        """Returns a dictionary with the attributes filled out, which can be used by the
        create_operator method"""
        if potential_variable_name in self._generated_variables.keys():
            return {"VariableName": potential_variable_name, "VariableId": self._generated_variables[potential_variable_name]}
        else:
            potential_variable_name = potential_variable_name.replace("'", '"')
            
            # we want to preserve the typing and not just turn every number into a string.
            # what if the user wants to do "8" + "9" to get "89"?
            # TODO add distinguishing feature to values to determine if they're a number or a string.
            if potential_variable_name.isdigit():
                # integer!
                potential_variable_name = int(potential_variable_name)
            else:
                try:
                    # trying to convert to float
                    potential_variable_name = float(potential_variable_name)
                except ValueError:
                    # whelp, i guess it wants to stay as a str. 
                    pass
            return {"Value": potential_variable_name}

    def get_variable_name_from_id(self, id: str):
        """Returns the variable name from the given id"""
        for i in self._generated_variables:
            if self._generated_variables[i] == id:
                return i

    def convert_expression(self, line: str):
        """Formats the expression to have no whitespace"""
        if type(line) is not str:
            return line
        line = "".join(line.split())
        for i in COMBINED_OPERATORS:
            index = line.find(i)
            if index != -1:
                variable_name = search(line, LEFT_ANY_OPERATOR).strip()
                right_side = line[index + 2:].strip()
                operator = COMBINED_OPERATORS[i]

                return variable_name + operator + right_side
        return line
    
    def convert_expression_boolean(self, line: str):
        """Formats the expression to have no whitespace
        and replaces boolean operators with a more processable type used by
        evaluate_boolean"""
        if type(line) is not str:
            # yeah i know the function LITERALLY ASKS FOR A STR
            return line
        line = "".join(line.split())
        for i in BOOLEAN_SUB:
            # line = line.replace(i, BOOLEAN_SUB[i])
            line = re.sub(fr"\b{i}\b", BOOLEAN_SUB[i], line)
        line = line.replace("==", BOOLEAN_SUB["=="])
        return line

    def get_operator(self, line: str, operator_order: list[str]):
        """Returns the first operator it finds (left to right)"""
        # FIXME, try to make operator find exact symbol, detects "==" instead of "="
        # note this is also why variable isn't compiling properly. 
        operator = ""
        index = -1
        for i in operator_order:
            if type(line) is not str:
                break
            
            line = line.replace("==", "`")

            # temp = line
            # temp = temp.replace("==", "")
            
            index = line.find(i)
            if index != -1:
                operator = i
                break
        return operator, index

    def __append_linked_list(self, expression: str, expression_to_use: str, op_index: int, operator: str, linked_list: list[dict], recursive_function):
        """Should not be used outside of self.evaluate and self.evaluate_boolean"""
        left = expression_to_use[:op_index]
        right = expression_to_use[op_index + 1:]

        left = re.split(r"[\/\*\+\-]", left)[-1]
        right = re.split(r"[\/\*\+\-]", right)[0]

        left = re.sub(r"[()]", "", left).strip()
        right = re.sub(r"[()]", "", right).strip()

        left_result = self.get_variable_table_for_operator(recursive_function(left, linked_list))
        right_result = self.get_variable_table_for_operator(recursive_function(right, linked_list))

        id_to_use = self.generate_id()
        expression = expression.replace("(" + left + operator + right + ")", id_to_use)
        if expression.find(left + operator + right) != -1:
            expression = expression.replace(left + operator + right, id_to_use)

        print("Appending", operator)

        linked_list.append(
            {
                "Operator": operator,
                "Value": [left_result, right_result],
                "Id": id_to_use,
            }
        )

        return recursive_function(expression, linked_list)

    def evaluate(self, expression: str, linked_list: list[dict]):
        """Updates the linked_list given with a list of parameters. This list reversed can be used
        repeatedly by create_operator to correctly follow bodmas"""
        operator, index = self.get_operator(expression, REVERSED_ORDER)
        
        print(operator, "found in", expression)
        # if operator == "=":
        #     # ignoring "=" operators. 
        #     expression = expression[index + 1:]
        #     operator, index = self.get_operator(expression, REVERSED_ORDER)

        expression_to_use = expression

        if index == -1:
            _, index = self.get_operator(expression, BOOLEAN_ORDER)
            if index != -1:
                print("BEFORE", expression_to_use)
                expression_to_use = self.evaluate_boolean(expression_to_use, linked_list)
                print("AFTER", expression_to_use)
                return expression_to_use
            else:
                return expression
            # return expression

        if expression_to_use == operator:
            Warning("This shouldn't happen - somehow have the expression the same as the operator?")
            return ""
        # yeah i know, lots of duplicate code here. but i'm too scared to refactor in case it breaks everything :(
        
        if operator == "(":
            # handling stuff in between brackets
            index = expression_to_use.rfind("(")
            expression_to_use = get_value_in_brackets(expression_to_use[index:])[0]

            # get the operator inside the bracket, if there is one.
            operator, op_index = self.get_operator(expression_to_use, REVERSED_ORDER)

            if op_index == -1:
                expression = expression.replace("(" + expression_to_use + ")", expression_to_use)
                return self.evaluate(expression, linked_list)

            expression = self.__append_linked_list(expression, expression_to_use, op_index, operator, linked_list, self.evaluate)
        else:
            expression = self.__append_linked_list(expression, expression_to_use, index, operator, linked_list, self.evaluate)

        
        return expression
    
    def evaluate_boolean(self, line: str, linked_list: list[dict]):
        """Similar to evaluate, but for boolean expressions only"""
        expression = line
        expression_to_use = expression
        operator, index = self.get_operator(expression, BOOLEAN_ORDER)

        if index == -1:
            # _, index = self.get_operator(expression, REVERSED_ORDER)
            # if index != -1:
            #     print("BEFORE", expression_to_use)
            #     expression_to_use = self.evaluate(expression_to_use, linked_list)
            #     print("AFTER", expression_to_use)
            #     return expression_to_use
            # else:
            #     return expression
            return expression
        if expression_to_use == operator:
            raise scratch_exceptions.Panic()
        
        if operator == "(":
            # handling stuff in between brackets
            index = expression_to_use.rfind("(")
            expression_to_use = get_value_in_brackets(expression_to_use[index:])[0]

            # get the operator inside the bracket, if there is one.
            operator, index = self.get_operator(expression_to_use, BOOLEAN_ORDER)

            if index == -1:
                return line

            expression = self.__append_linked_list(expression, expression_to_use, index, operator, linked_list, self.evaluate_boolean)

        elif operator == "!":
            right = expression_to_use[index + 1:]
            right = re.sub(r"[()]", "", right).strip()
            right_result = self.get_variable_table_for_operator(self.evaluate_boolean(right, linked_list))
            id_to_use = self.generate_id()
            expression = expression.replace(operator + right, id_to_use)

            linked_list.append(
                {
                    "Operator": operator,
                    "Value": [right_result, right_result],
                    "Id": id_to_use
                }
            )
            self.evaluate_boolean(expression, linked_list)
        else:
            expression = self.__append_linked_list(expression, expression_to_use, index, operator, linked_list, self.evaluate_boolean)
        return expression

    def generate_evaluation(self, line: str) -> tuple[str, bool]:
        """Wrapper function for self.evaluate and self.evaluate_boolean Returns the id of the root operator,
        to convieniently parent to a block."""

        # we NUKE anything left to the = sign
        if type(line) is str:
            if search(line, SINGLE_EQUAL):
                anchor = line.find("=")
                line = line[anchor + 1:].lstrip().rstrip()
        
        eval_list = []
        bool_list = []
        # this code generates a list which we can use to iterate through to create 
        # the string of operators in the correct order. 
        line = self.convert_expression(line)
        line = self.replace_variable_name_with_id(line)
        line = self.convert_expression_boolean(line)
        print("To convert:", line)
        # line = self.evaluate_boolean(line, linked_list)
        line = self.evaluate(line, eval_list)

        if eval_list == [] and bool_list == []:
            # if the list is empty, then that means the statement is a simple 
            # variable = variable 
            # or
            # variable = number

            formatted = self.convert_expression(line)

            return formatted, False
        else:
            # TODO attempt to fix issue with parenting operators to boolean operators. 
            # i.e. 4 + 5 == 4 becomes
            # 4 + (5 == 4)
            # instead of 
            # (4 + 5) == 4 in scratch.
            # UPDATE, EVEN AFTER THE WHOLE DEBACLE OF MERGING, IT STILL DOESN'T WORK

            # reverse, because we want to do lowest priority first. Scratch does top to bottom, list gives us bottom to top, so we want lowest
            # priority at the bottom.
            print("BEFORE", eval_list)
            bool_list.reverse()
            eval_list.reverse()
            print(eval_list)

            entire_eval = bool_list + eval_list

            print(entire_eval)

            prev_id = None
            # for now, the parent is none so we can manually assign it to any parent we want later. 

            root_operator = None


            for evaluation in entire_eval:
                if prev_id is None:
                    root_operator = evaluation["Id"]
                if evaluation["Operator"] == "。":
                    raise scratch_exceptions.UnsupportedFeature("!= (please use == instead)")
                
                # success_1 = False
                # success_2 = False
                # if evaluation["Value"][0].get("Value", None) is not None:
                #     root_operator_1, success_1 = self.generate_evaluation(evaluation["Value"][0]["Value"])
                #     if success_1:
                #         evaluation["Value"][0] = self.get_variable_table_for_operator(root_operator_1)

                # if evaluation["Value"][1].get("Value", None) is not None:
                #     root_operator_2, success_2 = self.generate_evaluation(evaluation["Value"][1]["Value"])
                #     if success_2:
                #         evaluation["Value"][1] = self.get_variable_table_for_operator(root_operator_2)
                
                if BOOLEAN_OPERATORS.get(evaluation["Operator"], None) is None:
                    # if not a boolean operator, create a non-boolean operator. 
                    parent = self.create_operator(OPERATORS[evaluation["Operator"]], evaluation["Value"], prev_id, evaluation["Id"])
                else:
                    parent = self.create_operator(BOOLEAN_OPERATORS[evaluation["Operator"]], evaluation["Value"], prev_id, evaluation["Id"])

                self.operator_parent_to(self._block_dict[root_operator], root_operator, parent)

                prev_id = evaluation["Id"]
                # if success_1:
                #     self.operator_parent_to(self._block_dict[root_operator_1], root_operator_1, parent)
                # if success_2:
                #     self.operator_parent_to(self._block_dict[root_operator_2], root_operator_2, parent)

            return root_operator, True

    def morph_if_to_elif(self, if_id: str):
        """Morphs an existing control_if into a control_if_else
        which is used by create_block to parent to SUBSTACK2 if needed"""
        if_statement = self._block_dict[if_id]
        if_statement["opcode"] = "control_if_else"
        if_statement["inputs"]["SUBSTACK2"] = [
            2,
            "TEMP"
        ]
        self._most_recent_block[self._indent_level + 1] = if_id

    def if_statement(self, line: str, fake_indent: bool = None):
        """Creates an if statement from the given statement, 
        to forcefully parent to an else block, set fake_indent to True"""
        parent = self._most_recent_block[self._indent_level]
        block_id = self.generate_id()
        self.create_block("control_if", {"CONDITION": [2, "TEMP"], "PARENT_TO_ELIF": fake_indent}, parent, block_id)
        self._most_recent_block[self._indent_level + 1] = block_id # this is for blocks inside the stack to parent to.
        self._most_recent_block[self._indent_level] = block_id # this is for blocks outside of the stack to parent to.
        
        line = line.lstrip() 
        if line[:2] == "if":
            statement = line[2:].rstrip()[:-1]
        else:
            statement = line[4:].rstrip()[:-1]
        # we get everything between the "if" and the ":"
        # if the string we get from this is invalid, then there would've been a syntax error anyway.
        linked_list = []
        self.evaluate_boolean(statement, linked_list)
        linked_list.reverse()
        if linked_list == []:
            raise scratch_exceptions.UnsupportedFeature("no comparators in boolean statement")
        
        prev_id = block_id
        for evaluation in linked_list:
            if evaluation["Operator"] == ".":
                raise scratch_exceptions.UnsupportedFeature("!= (please use == instead)")
            success_1 = False
            success_2 = False
            if evaluation["Value"][0].get("Value", None) is not None:
                root_operator_1, success_1 = self.generate_evaluation(evaluation["Value"][0]["Value"])
                if success_1:
                    evaluation["Value"][0] = self.get_variable_table_for_operator(root_operator_1)

            if evaluation["Value"][1].get("Value", None) is not None:
                root_operator_2, success_2 = self.generate_evaluation(evaluation["Value"][1]["Value"])
                if success_2:
                    evaluation["Value"][1] = self.get_variable_table_for_operator(root_operator_2)


            parent = self.create_operator(BOOLEAN_OPERATORS[evaluation["Operator"]], evaluation["Value"], prev_id, evaluation["Id"])
            prev_id = evaluation["Id"]

            if success_1:
                self.operator_parent_to(self._block_dict[root_operator_1], root_operator_1, parent)
            if success_2:
                self.operator_parent_to(self._block_dict[root_operator_2], root_operator_2, parent)
  
        return block_id

    def get_function_name(self, line: str):
        for i in self._functions:
            if line.find(i) != -1:
                return i
        return -1

    def compile(self):
        global_lists = {}
        global_variables = {} # store in studio
        local_lists = {}
        local_variables = {} # store in sprite

        studio_index = 0 # default is 0. Shouldn't change if we're targetting the studio. 
        sprite_index = -1 # target index
        sprite_is_studio = False
        sprite_variable = ""

        self._most_recent_block = {0: self.create_block("event_whenflagclicked", {}, False)}

        for line_number, v in enumerate(self._target_code):
            # getting current sprite
            v = v.replace("_", "")
            self._line_number = line_number
            self._indent_level = (len(v) - len(v.lstrip())) // 4
            if self._indent_level not in self._most_recent_block.keys():
                self._most_recent_block[self._indent_level] = None

            tokens = get_tokens(v)
            function_found = self.get_function_name(v)
            variable_name, _ = get_variable_name(v)

            if sprite_variable == "":
                if "scratchproject.Sprite" in v:
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
                    self._generated_variables[sprite_variable] = "PY_COMPILER"

                elif "scratchproject.Studio" in v:
                    if sprite_variable: raise scratch_exceptions.TooManySprites
                    
                    sprite_variable, _ = get_variable_name(v)
                    sprite_is_studio = True
                    sprite_index = studio_index
                    self._generated_variables[sprite_variable] = "PY_COMPILER"
            if "def" in tokens:                
                function_name = tokens[tokens.index("def") + 1]
                # because I'm not expecting for there to be children oustide the inner stack for definitions, 
                # i don't do self._most_recent_block[self._indent_level]
                self._most_recent_block[self._indent_level + 1] = self.create_block("procedures_definition", {}, False)
                function_id = self.create_block("procedures_prototype", {"Name": function_name}, self._most_recent_block[self._indent_level + 1])
                param_string = get_value_in_brackets(v)[0]
                if not param_string:
                    param_list = []
                else:
                    # generate a tuple of all parameters. 
                    param_list = (''.join(param_string.split())).split(",")
                params = {}

                if len(param_list) > 0 and param_list[0] != '':
                    for i in param_list:
                        # we split each param into a param_name, and param_type
                        split_param = i.split(":")
                        param_name = split_param[0]
                        param_type = split_param[1]

                        if TYPES.get(param_type, None) is None:
                            # scratch only supports floats, ints, strings.
                            # we can't directly use a list, which is troubling. 
                            raise scratch_exceptions.InvalidArgumentType(param_type)
                        
                        # creating the actual input
                        argument_id = self.create_argument(param_type, param_name, function_id)
                        params[param_name] = [argument_id, param_type, param_name, function_id]
                        
                # creating list of params for this specific function so we can use it in variables later.
                self._functions[function_name] = function_id
                self._function_variables[self._indent_level + 1] = params     
            elif "if" in tokens:
                self._most_recent_if[self._if_layers + self._indent_level] = self.if_statement(v)
            elif "else" in tokens:
                # generally the previous recent block on the same indent should always be IF.
                # this might be false if it's a try and except, but we don't need to worry
                # about that because scratch doesn't support it.
                self.morph_if_to_elif(self._most_recent_block[self._indent_level])
                pass
            elif "elif" in tokens:
                self.morph_if_to_elif(self._most_recent_block[self._indent_level])
                self._if_layers += 1
                self.if_statement(v, True)
            elif "for" in tokens:
                # we anchor at "in"
                anchor = tokens.index("in")
                if tokens[anchor + 1] == "range":
                    in_brackets = get_value_in_brackets(v)[0].split(",")
                    # regular for loop
                    loop1 = tokens[anchor - 1]
                    number_of_arguments = len(in_brackets)
                    if number_of_arguments == 1:
                        # 0 up to n
                        start = 0
                        end = in_brackets[0]
                        step = 1
                    elif number_of_arguments == 2:
                        # x up to y
                        start = in_brackets[0]
                        end = in_brackets[1]
                        step = 1
                    else:
                        # x up to y w/ step
                        start = in_brackets[0]
                        end = in_brackets[1]
                        step = in_brackets[2]

                    root_operator, success = self.generate_evaluation(f"({end}) - ({start})")
                    # success should always be true here. if not, wellllllll
                    if not success:
                        raise SyntaxError("range() is empty")

                    variable_id = self.generate_id()

                    # append the generated variable to the variable list
                    self._generated_variables[loop1] = variable_id 
                    local_variables[variable_id] = [loop1, 0]

                    # since scratch only "repeats" we have to emulate this behaviour by literally creating an "i" variable (or whatever the user names it)
                    start_root_operator, success = self.generate_evaluation(str(start))

                    self._most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Value": start, "VariableId": variable_id, "Name": loop1}, self._most_recent_block[self._indent_level])
                    if success:
                        self.operator_parent_to(self._block_dict[start_root_operator], start_root_operator, self._most_recent_block[self._indent_level])
                    self._most_recent_block[self._indent_level] = self.create_block("control_repeat", {"TIMES": None}, self._most_recent_block[self._indent_level])
                    self._most_recent_block[self._indent_level + 1] = self._most_recent_block[self._indent_level]
                    # we evaluate the repeats and append it to the control_repeat
                    self.operator_parent_to(self._block_dict[root_operator], root_operator, self._most_recent_block[self._indent_level])
                    self._indent_level += 1
                    # evaluate the "step"
                    self.create_variable_add_block(str(step), variable_id, "changevariableby", self._most_recent_block[self._indent_level])
                    self._indent_level -= 1
                elif tokens[anchor + 1] == "enumerate":
                    # enumerate loop
                    loop1 = tokens[anchor - 3]
                    loop2 = tokens[anchor - 1]
                    pass
                else:
                    # likely iterating through a list or variable
                    loop1 = tokens[anchor - 1]
                    variable_id = self.generate_id()
                    self._most_recent_block[self._indent_level] = self.create_block("control_repeat", {"TIMES": None}, self._most_recent_block[self._indent_level])
                    id, success = self.generate_evaluation(tokens[anchor + 1])
                    operator_id = self.create_operator("operator_length", [{"Value": id}, {"Value": id}], self._most_recent_block[self._indent_level])
                    self.operator_parent_to(self._block_dict[operator_id], operator_id, self._most_recent_block[self._indent_level])
                    # append the generated variable to the variable list
                    self._generated_variables[loop1] = variable_id 
                    local_variables[variable_id] = [loop1, 0]
                    self._most_recent_block
                    pass
            elif function_found != -1:
                function_id = self._functions[function_found]
                args = get_value_in_brackets(v)[0]
                if not param_string:
                    param_list = []
                else:
                    # generate a tuple of all parameters. 
                    param_list = (''.join(args.split())).split(",")
                    for i, param in enumerate(param_list):
                        root_operator, success = self.generate_evaluation(param.strip('"'))
                        param_list[i] = root_operator
                self._most_recent_block[self._indent_level] = self.create_block("procedures_call", {"FunctionId": function_id, "Args": param_list}, self._most_recent_block[self._indent_level])
            elif variable_name is not None:
                if variable_name not in self._generated_variables.keys():
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
                                According to scratch wiki, global variables are stored in the stage
                                """
                                global_variables[variable_id] = [variable_name, 0]
                            else:
                                local_variables[variable_id] = [variable_name, 0]
                        self._generated_variables[variable_name] = variable_id
                if variable_name != sprite_variable:
                    variable_id = self._generated_variables[variable_name]
                    self.create_variable_add_block(v, variable_id, "setvariableto", self._most_recent_block[self._indent_level])

            self._prev_line_number = self._line_number

        if not sprite_is_studio:
            # adding variables created in script
            self._result_file_code["targets"][sprite_index]["variables"] = {} # we clear the previous variables because we don't want 
                                                                              # previously similar variable names to compete
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
    print("COMPILING", python_file_name)
    start_time = time.time()
    compiler = Compiler(python_file_name, scratch_file_name)
    compiler.compile()
    print("Finished, time took:", time.time() - start_time)
    # translate(python_code, scratch_file_name, project_json)

main()
