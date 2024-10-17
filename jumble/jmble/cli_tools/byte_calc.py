""" Simple calculate for various data storage units. """

import sys
import re

from typing import Literal

PREFIXES = {
    "Ki": 1024,
    "K": 1000,
    "Mi": 1024**2,
    "M": 1000**2,
    "Gi": 1024**3,
    "G": 1000**3,
    "Ti": 1024**4,
    "T": 1000**4,
    "Pi": 1024**5,
    "P": 1000**5,
    "Ei": 1024**6,
    "E": 1000**6,
}

SUFFIXES = {
    "b": 1,
    "B": 8,
}

# UNIT_PATTERN = re.compile(r"(?:(\d+)|(\d+\.\d+))([a-zA-Z]+)?")
UNIT_PATTERN = re.compile(r"(?:(\d+\.\d+)|(\d+))(\w+)?")
OPERATOR_PATTERN = re.compile(r"([+\-*/])")
OUTPUT_UNIT = "MiB"


def is_numeric(value: str) -> bool:
    if value.isnumeric():
        return True
    if value[0] in "+-" and is_numeric(value[1:]):
        return True
    if value.count(".") == 1:
        return value.replace(".", "").isnumeric()
    return False


def find_parentheses(expression: str) -> list[tuple[int]]:
    """Find the matching parentheses in an expression.

    Args:
        expression (str): The expression to search.

    Raises:
        ValueError: If there are unmatched parentheses.

    Returns:
        list[tuple[int]]: The start and end positions of the parentheses.
    """

    stack = []
    matches = []
    for i, char in enumerate(expression):
        if char == "(":
            stack.append(i)
        elif char == ")" and stack:
            start = stack.pop()
            matches.append((start, i))

    if not matches and not stack:
        matches.append((0, len(expression) - 1))
    if not matches and stack:
        raise ValueError("Unmatched parentheses")
    return matches


def extract_nested_parentheses(expression: str) -> list[str]:
    positions = find_parentheses(expression)
    groups = [expression[start : end + 1] for start, end in positions]
    if expression not in groups:
        groups.append(expression)
    return groups


def split_unit(term: str) -> tuple[float, str]:

    match = UNIT_PATTERN.match(term)
    if not match:
        raise ValueError(f"Invalid term: {term}")

    groups = tuple(group for group in match.groups() if group)

    value, unit = groups if len(groups) == 2 else (groups[0], "B")

    if isinstance(value, str) and is_numeric(value):
        value = float(value)
    else:
        raise ValueError(f"Invalid value: {value}")

    return value, unit


def to_bits(term: str) -> float:
    value, unit = split_unit(term)
    prefix_str = r"|".join(PREFIXES.keys())
    suffix_str = r"|".join(SUFFIXES.keys())
    pattern = rf"(?:({prefix_str})?({suffix_str})?)"

    match = re.match(pattern, unit)

    if not match:
        raise ValueError(f"Invalid unit: {unit}")

    unit, bits = match.groups()
    bits = SUFFIXES.get(bits, 8)
    factor = PREFIXES.get(unit, 1)

    return value * factor * bits


def eval_expression(expression: str) -> str | float:

    print("expression:", expression)
    expression = expression.replace(" ", "").replace("(", "").replace(")", "")

    terms = OPERATOR_PATTERN.split(expression)
    print("terms:", terms)
    if len(terms) == 1:
        return to_bits(terms[0])

    result = to_bits(terms[0])
    operator = None

    for term in terms[1:]:
        if term in "+-*/":
            operator = term
        else:
            value = to_bits(term)
            if operator == "+":
                result += value
            elif operator == "-":
                result -= value
            elif operator == "*":
                result *= value
            elif operator == "/":
                result /= value
    return f"{result}b"


def calculate(expression: str) -> float:
    expressions = extract_nested_parentheses(expression)
    result = None
    prev_expression = None
    pattern = re.compile(r"(.*?)(\".*?\")(.*)")
    print("expressions:", expressions)
    for expression in expressions:
        if result is not None:
            expression = expression.replace(prev_expression, str(result))
        result = eval_expression(expression)
        prev_expression = expression

    return result


def convert_to_unit(value: float | str, unit: str, precision: int = 2) -> str:
    unit_bits = to_bits(f"1{unit}")

    value = to_bits(value) if isinstance(value, str) else value

    size = round(value / unit_bits, precision)

    return f"{size}{unit}"


def evaluate(expression: str, unit: str = OUTPUT_UNIT, precision: int = 2) -> str:
    result = calculate(expression)
    return convert_to_unit(result, unit, precision)


test_str = "2Kb * ((3Kb - 2Kb) + 1Kb)"
test_str_2 = "2.5KiB"

print(evaluate(test_str, "Kb"))
