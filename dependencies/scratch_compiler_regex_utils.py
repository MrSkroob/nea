import tokenize
from io import BytesIO

import re 


BETWEEN_BRACKETS = r"(?<=\()(.*?)(?=\))"

LEFT_ANY_OPERATOR = r".+?(?=\S{1}=)"

LEFT_OPERATOR_EQUAL = r".+?(?=\=)"
LEFT_OPERATOR_PLUS = r".+?(?=\+=)"
LEFT_OPERATOR_MINUS = r".+?(?=\-=)"
LEFT_OPERATOR_MUL = r".+?(?=\*=)"
LEFT_OPERATOR_DIV = r".+?(?=\/=)"
LEFT_OPERATOR_MOD = r".+?(?=\%=)"
LEFT_BRACKET = r".+?(?=\[)"

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
    LEFT_BRACKET,
    LEFT_OPERATOR_EQUAL,# this is ordered at the back so we check other operators first. 
                        # not doing this will make += match to =, resulting in the variable name being
                        # "variable_1 +"
]

GET_RIGHT_SIDE = [
    RIGHT_OPERATOR_PLUS,
    RIGHT_OPERATOR_MINUS,
    RIGHT_OPERATOR_MUL,
    RIGHT_OPERATOR_DIV,
    RIGHT_OPERATOR_MOD,
    RIGHT_OPERATOR_EQUAL,
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