# testing for basic idea of adding blocks to a scratch project.
# this one is for a basic block.
import tokenize

from io import BytesIO

import json
import zipfile
import re
import copy
from dependencies import scratch_exceptions

# useful regexes
BETWEEN_BRACKETS = r"(?<=\()(.*?)(?=\))"

LEFT_ANY_OPERATOR = r".+?(?=\S{1}=)"

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

BOOLEAN_OPERATORS = {
    "?": ".", # I'll need special behaviour for this BECAUSE OF COURSE I DO
    "=": "operator_equals",
    "<": "operator_lt",
    ">": "operator_gt",
    "!": "operator_not",
    "&": "operator_and",
    "|": "operator_or"
}


BOOLEAN_SUB = {
    "!=": "?",
    "==": "=",
    "<": "<",
    ">": ">",
    "not": "!",
    "and": "&",
    "or": "|"
}


BOOLEAN_ORDER = [
    "(",
    "?",
    "=",
    "<",
    ">",
    "!",
    "&",
    "|"
]


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


COMBINED_OPERATORS = {
    "+=": "+",
    "-=": "-",
    "*=": "*",
    "/=": "/",
    "%=": "%",
    "//=": "//"
    # "**=": "**" scratch doesn't natively have indices multiplication yet
}


ORDER = [
    # highest top, lowest bottom
    "=",
    "-",
    "+",
    "//",
    "/",
    "*",
    "**",
    "(",
]


REVERSED_ORDER = [
    "(",
    "**",
    "*",
    "/",
    "//",
    "+",
    "-",
    "="
]


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
    expression_bytes = line.strip().encode()
    tokens = [i.string for i in tokenize.tokenize(BytesIO(expression_bytes).readline)]
    return tokens[1:]


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

def get_operators(line: str):
    operators = []
    for i in OPERATOR_TYPE:
        if i in line:
            operators.append(i)
    return operators


def get_variable_value(line: str):
    for i in GET_RIGHT_SIDE:
        match = search(line, i)
        expression = i
        if match is not None: break
    return match, expression


def get_value_in_brackets(line: str):
    result = re.findall(BETWEEN_BRACKETS, line)
    return result


class Compiler():
    def __init__(self, file_to_compile: str, file_to_compile_to: str) -> None:
        self._target_code = load_python_file(file_to_compile)
        self._result_file_code = load_scratch_project(file_to_compile_to)

        self._compile_from = file_to_compile
        self._compile_to = file_to_compile_to

        self._sprite_list = [i["name"] for i in self._result_file_code["targets"]]
        self._most_recent_if = {}
        # self._if_statements = [] # list to iterate backwards to find correct parent. 
        self._function_variables = {}
        self._functions = {}
        self._generated_variables = {}
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
        return id.find("PY_TO_SCRATCH") != -1

    def is_parameter(self, param_name: str):
        try:
            return param_name in self._function_variables[self._indent_level]
        except KeyError:
            return False

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
            if self.is_id(value["Value"]) or is_argument:
                # check if value exists as an argument in a function
                if is_argument:
                    # this should always be true honestly
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
        """This should not be used"""
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
            block_data_copy["parent"] = parent
            if self._block_dict[parent]["opcode"] == "control_if":
                self._block_dict[parent]["inputs"]["CONDITION"][1] = block_id
            elif self._block_dict[parent]["opcode"] == "operator_not":
                self._block_dict[parent]["inputs"]["OPERAND"] = [
                    2,
                    block_id
                ]
            elif self._block_dict[parent]["opcode"] in BOOLEAN_OPERATOR_LIST:
                # check if operator is a boolean operator
                self.assign_to_boolean_operator(parent, block_id)
            else:
                # operator is NOT a boolean operator
                try:
                    self._block_dict[parent]["inputs"]["VALUE"][1] = block_id
                except KeyError:
                    # i apologise to myself in the future for all this terrible code
                    self.assign_to_default_operator(parent, block_id)
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
        else:
            block_data_copy["inputs"] = {
                "OPERAND1": value1,
                "OPERAND2": value2
            }
        block_data_copy["topLevel"] = False

        del block_data_copy["x"]
        del block_data_copy["y"]

        return block_id


    def parent_to(self, block_data_copy: dict, block_args: dict, child: str, parent: str):
        print("START PARENT=======")
        block_data_copy["topLevel"] = False
        parent_block = self._block_dict[parent]
        print("parent:", parent_block["opcode"], "child:", block_data_copy["opcode"])
        print("current indent level:", self._indent_level)
        block_data_copy["parent"] = parent

        next_indent = self._most_recent_block.get(self._indent_level + 1, None)
        previous_indent = self._most_recent_block.get(self._indent_level - 1, None)

        if parent_block["opcode"] == "control_if":
            if previous_indent == parent or next_indent is None: 
                # this means that we are parenting inside of the substack
                parent_block["inputs"]["SUBSTACK"][1] = child
                print("inside stack, if")
            else:
                # parent to outside the substack
                block_data_copy["parent"] = self._most_recent_if[self._indent_level]
                self._block_dict[self._most_recent_if[self._indent_level]]["next"] = child
                print("outside stack, if")
        elif parent_block["opcode"] == "control_if_else":
            if block_args.get("PARENT_TO_ELIF", None) is not None:
                print("inside, forced, elif")
                parent_block["inputs"]["SUBSTACK2"][1] = child
            elif previous_indent == parent or next_indent is None:
                # this means that we are parenting inside of the substack
                if parent_block["inputs"]["SUBSTACK2"][1] == "TEMP":
                    print("inside, elif")
                    parent_block["inputs"]["SUBSTACK2"][1] = child
                else:
                    print("wtf?")
                    parent_block["next"] = child
            else:
                # parent to outside the substack
                print("outside stack, elif")
                parent_block["next"] = child
        else:
            print("normal next")
            self._if_layers = self._indent_level
            parent_block["next"] = child
        print("END PARENT====")

    
    def create_block(self, opcode: str, block_args: dict, parent: str | bool, id_to_use=None):
        if id_to_use is None:
            block_id = self.generate_id()
        else:
            block_id = id_to_use
        block_data_copy = copy.deepcopy(BLOCK_DATA)
        block_data_copy["opcode"] = opcode
        # things might get a lil' hard coded in here >:)
        if parent is None:
            parent = self._most_recent_block[self._indent_level - 1]
        if parent is not False:
            self.parent_to(block_data_copy, block_args, block_id, parent)
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
            # del block_data_copy["x"]
            # del block_data_copy["y"]
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

        self._block_dict[block_id] = block_data_copy
        return block_id


    def get_variable_table_for_operator(self, potential_variable_name: str):
        """Returns a dictionary with the attributes filled out"""
        if potential_variable_name in self._generated_variables.keys():
            return {"VariableName": potential_variable_name, "VariableId": self._generated_variables[potential_variable_name]}
        else:
            potential_variable_name = potential_variable_name.replace("'", "")
            potential_variable_name = potential_variable_name.replace('"', "")
            return {"Value": potential_variable_name}


    def convert_expression(self, line: str):
        """Formats the expression to have no whitespace"""
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
        and replaces boolean operators with a more processable type"""
        line = "".join(line.split())
        for i in BOOLEAN_SUB:
            line = line.replace(i, BOOLEAN_SUB[i])
        return line     

    def get_operator(self, line: str, operator_order: list[str]):
        operator = ""
        index = -1
        for i in operator_order:
            index = line.find(i)
            if index != -1:
                operator = i
                break
        return operator, index

    def evaluate(self, line: str, linked_list: list[dict]):
        expression = self.convert_expression(line)
        # expression = expression.replace("()", "") not sure if this line is needed.
        operator, index = self.get_operator(expression, REVERSED_ORDER)
        
        if operator == "=":
            # ignoring "=" operators. 
            expression = expression[index + 1:]
            operator, index = self.get_operator(expression, REVERSED_ORDER)

        expression_to_use = expression

        if index == -1:
            return expression_to_use

        if expression_to_use == operator:
            Warning("This shouldn't happen - somehow have the expression the same as the operator?")
            return ""
        # yeah i know, lots of duplicate code here. but i'm too scared to refactor in case it breaks everything :(
        
        if operator == "(":
            # handling stuff in between brackets
            index = expression_to_use.rfind("(")
            expression_to_use = get_value_in_brackets(expression_to_use[index:])[0]

            # get the operator inside the bracket, if there is one.
            operator, index = self.get_operator(expression_to_use, REVERSED_ORDER)

            left = expression_to_use[:index]
            right = expression_to_use[index + 1:]

            left = re.split(r"[\/\*\+\-]", left)[-1]
            right = re.split(r"[\/\*\+\-]", right)[0]

            left = re.sub(r"[()]", "", left).strip()
            right = re.sub(r"[()]", "", right).strip()

            left_result = self.get_variable_table_for_operator(self.evaluate(left, linked_list))
            right_result = self.get_variable_table_for_operator(self.evaluate(right, linked_list))

            id_to_use = self.generate_id()
            expression = expression.replace("(" + left + operator + right + ")", id_to_use)
            if expression.find(left + operator + right):
                expression = expression.replace(left + operator + right, id_to_use)

            linked_list.append(
                {
                    "Operator": operator,
                    "Value": [left_result, right_result],
                    "Id": id_to_use,
                }
            )
            self.evaluate(expression, linked_list)
        else:
            left = expression_to_use[:index]
            right = expression_to_use[index + 1:]

            left = re.split(r"[\/\*\+\-]", left)[-1]
            right = re.split(r"[\/\*\+\-]", right)[0]

            left = re.sub(r"[()]", "", left).strip()
            right = re.sub(r"[()]", "", right).strip()

            left_result = self.get_variable_table_for_operator(self.evaluate(left, linked_list))
            right_result = self.get_variable_table_for_operator(self.evaluate(right, linked_list))

            id_to_use = self.generate_id()

            expression = expression.replace(left + operator + right, id_to_use)

            linked_list.append(
                {
                    "Operator": operator,
                    "Value": [left_result, right_result],
                    "Id": id_to_use,
                }
            )
            self.evaluate(expression, linked_list)

        return expression
    

    def evaluate_boolean(self, line: str, linked_list: list[dict]):
        expression = self.convert_expression_boolean(line)
        operator, index = self.get_operator(expression, BOOLEAN_ORDER)
        expression_to_use = expression

        if expression_to_use == "True":
            raise scratch_exceptions.UnsupportedFeature("Bare booleans. (Try doing 1 == 1 instead)")
        elif expression_to_use == "False":
            raise scratch_exceptions.UnsupportedFeature("Bare booleans. (Try doing 1 != 1 instead)")

        if index == -1:
            return line
        
        if expression_to_use == operator:
            Warning("This shouldn't happen")
            return ""
        if operator == "(":
            # handling stuff in between brackets
            index = expression_to_use.rfind("(")
            expression_to_use = get_value_in_brackets(expression_to_use[index:])[0]

            # get the operator inside the bracket, if there is one.
            operator, index = self.get_operator(expression_to_use, BOOLEAN_ORDER)

            left = expression_to_use[:index]
            right = expression_to_use[index + 1:]
            
            left = re.split(r"[\?\=\<\>\!\&\|]", left)[-1]
            right = re.split(r"[\?\=\<\>\!\&\|]", right)[0]

            left = re.sub(r"[()]", "", left).strip()
            right = re.sub(r"[()]", "", right).strip()

            left_result = self.get_variable_table_for_operator(self.evaluate_boolean(left, linked_list))
            right_result = self.get_variable_table_for_operator(self.evaluate_boolean(right, linked_list))

            id_to_use = self.generate_id()
            expression = expression.replace("(" + left + operator + right + ")", id_to_use)
            if expression.find(left + operator + right):
                expression = expression.replace(left + operator + right, id_to_use)

            linked_list.append(
                {
                    "Operator": operator,
                    "Value": [left_result, right_result],
                    "Id": id_to_use,
                }
            )
            self.evaluate_boolean(expression, linked_list)
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
            left = expression_to_use[:index]
            right = expression_to_use[index + 1:]

            left = re.split(r"[\?\=\<\>\!\&\|]", left)[-1]
            right = re.split(r"[\?\=\<\>\!\&\|]", right)[0]

            left = re.sub(r"[()]", "", left).strip()
            right = re.sub(r"[()]", "", right).strip()

            left_result = self.get_variable_table_for_operator(self.evaluate_boolean(left, linked_list))
            right_result = self.get_variable_table_for_operator(self.evaluate_boolean(right, linked_list))

            id_to_use = self.generate_id()

            expression = expression.replace(left + operator + right, id_to_use)

            linked_list.append(
                {
                    "Operator": operator,
                    "Value": [left_result, right_result],
                    "Id": id_to_use,
                }
            )
            self.evaluate_boolean(expression, linked_list)

        return expression
    

    def morph_if_to_elif(self, if_id: str):
        if_statement = self._block_dict[if_id]
        if_statement["opcode"] = "control_if_else"
        if_statement["inputs"]["SUBSTACK2"] = [
            2,
            "TEMP"
        ]
        self._most_recent_block[self._indent_level + 1] = if_id


    def if_statement(self, line: str, fake_indent: bool = None):
        # self._most_recent_block[self._indent_level + 1] = None
        # indent_parent = parent
        parent = self._most_recent_block[self._indent_level]
        block_id = self.generate_id()
        self.create_block("control_if", {"CONDITION": [2, "TEMP"], "PARENT_TO_ELIF": fake_indent}, parent, block_id)
        self._most_recent_block[self._indent_level + 1] = block_id
        self._most_recent_block[self._indent_level] = block_id
        
        # self._most_recent_block[self._indent_level + 1] = block_id
        line = line.lstrip() 
        if line[:2] == "if":
            statement = line[2:].rstrip()[:-1]
        else:
            statement = line[4:].rstrip()[:-2]
        # we get everything between the "if" and the ":"
        # if the string we get from this is invalid, then there would've been a syntax error anyway.
        linked_list = []
        self.evaluate_boolean(statement, linked_list)
        linked_list.reverse()
        if linked_list == []:
            raise scratch_exceptions.UnsupportedFeature("no comparators in boolean statement")
        
        prev_id = block_id
        # prev_id = self._most_recent_block[self._indent_level]
        for evaluation in linked_list:
            if evaluation["Operator"] == ".":
                raise scratch_exceptions.UnsupportedFeature("!= (please use == instead)")
            self.create_operator(BOOLEAN_OPERATORS[evaluation["Operator"]], evaluation["Value"], prev_id, evaluation["Id"])
            prev_id = evaluation["Id"]
        return block_id
        # new variation of the "self.evaluate()" method. 

    def get_parent_from_if_stack(self, most_recent_if_statement: str):
        """Method which appends a block to the elif stack"""
        root = self._block_dict[most_recent_if_statement]
        if root["opcode"] == "control_if" and root["inputs"]["SUBSTACK"][1] != "TEMP":
            return most_recent_if_statement
        elif root["opcode"] == "control_if_else" and root["inputs"]["SUBSTACK2"][1] != "TEMP":
            return self.get_parent_from_if_stack(root["inputs"]["SUBSTACK2"][1])
        else:
            return most_recent_if_statement

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

            variable_name, _ = get_variable_name(v)
            if "def" in tokens:                
                function_name = tokens[tokens.index("def") + 1]
                self._most_recent_block[self._indent_level + 1] = self.create_block("procedures_definition", {}, False)
                function_id = self.create_block("procedures_prototype", {"Name": function_name}, self._most_recent_block[self._indent_level + 1])
                param_string = get_value_in_brackets(v)[0]
                if not param_string:
                    param_list = []
                else:
                    param_list = (''.join(param_string.split())).split(",")
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
                        params[param] = [argument_id, param_type, param, function_id]
                        
                # creating list of params for this specific function so we can use it in variables later.
                self._function_variables[self._indent_level + 1] = params
            elif "if" in tokens:
                self._most_recent_if[self._if_layers] = self.if_statement(v)
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
                pass
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
                                According to scratch wiki, global variables are stored in the stage. So this isn't a hack okay!!!!
                                """
                                global_variables[variable_id] = [variable_name, 0]
                            else:
                                local_variables[variable_id] = [variable_name, 0]
                        self._generated_variables[variable_name] = variable_id
                if variable_name != sprite_variable:
                    linked_list = []
                    # this code generates a list which we can use to iterate through to create 
                    # the string of operators in the correct order. 
                    self.evaluate(v, linked_list)
                    if linked_list == []:
                        # if the list is empty, then that means the statement is a simple 
                        # variable = variable 
                        # or
                        # variable = number
                        formatted = self.convert_expression(v)
                        _, index = self.get_operator(formatted, ORDER)

                        if index != -1:
                            # honestly if this isn't true, then there should be a syntax error anyway.
                            right = formatted[index + 1:]

                            if right in self._function_variables.keys():
                                pass
                            value = self.get_variable_table_for_operator(right)
                            value["Name"] = variable_name
                            if self.is_parameter(value["Value"]):
                                # we check if the "value" is part of the function parameter
                                root = self._function_variables[self._indent_level][value["Value"]]
                                # pre-generate id
                                id_to_use = self.generate_id()
                                value["Value"] = id_to_use
                                value["OperatorId"] = id_to_use
                                self._most_recent_block[self._indent_level] = self.create_block("data_setvariableto", value, self._most_recent_block[self._indent_level])
                                
                                # because of the way I coded this, we have to parent the argument after creating the block. 
                                # makes sense though, you can't have children if the parent doesn't exist.
                                argument_id = self.create_argument(root[1], root[2], self._most_recent_block[self._indent_level], id_to_use)
                                self._block_dict[argument_id]["shadow"] = False
                            else:
                                self._most_recent_block[self._indent_level] = self.create_block("data_setvariableto", value, self._most_recent_block[self._indent_level])
                    else:
                        self._most_recent_block[self._indent_level] = self.create_block("data_setvariableto", {"Name": variable_name, "VariableId": self._generated_variables[variable_name], "OperatorId": "TEMP"}, self._most_recent_block[self._indent_level])
                        # reverse, because we want to do lowest priority first. Scratch does top to bottom, list gives us bottom to top, so we want lowest
                        # priority at the bottom.
                        linked_list.reverse()

                        prev_id = self._most_recent_block[self._indent_level]
                        # we have to parent this to something, right?
                        for evaluation in linked_list:
                            # iterate through, and simply create an operator using the data provided. 
                            self.create_operator(OPERATORS[evaluation["Operator"]], evaluation["Value"], prev_id, evaluation["Id"])
                            prev_id = evaluation["Id"]

            self._prev_line_number = self._line_number

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
