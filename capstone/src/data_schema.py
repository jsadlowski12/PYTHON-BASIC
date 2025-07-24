import os
import json
import logging
import sys

from capstone.src.constants import VALID_DATA_TYPES, VALID_RAND_INSTRUCTION_DATA_TYPES
from capstone.src.exception_utils import error_and_exit

def load_json_data_schema(schema_input: str) -> dict[str, str]:
    if os.path.isfile(schema_input):
        try:
            with open(schema_input, 'r') as f:
                schema = json.load(f)
            logging.info(f"JSON schema successfully loaded from file: {schema_input}")
            return schema
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to load schema from file '{schema_input}': {e}")
            sys.exit(1)

    if schema_input.endswith('.json') or os.path.sep in schema_input:
        logging.error(f"JSON schema file not found: {schema_input} (Current directory: {os.getcwd()})")
        sys.exit(1)

    try:
        schema = json.loads(schema_input)
        logging.info("JSON schema successfully parsed from command line input")
        return schema
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse schema as JSON string: {e}")
        logging.error("Make sure to properly escape quotes in command line JSON")
        sys.exit(1)

def validate_data_schema(schema: dict[str, str]) -> dict[str, str]:
    if not isinstance(schema, dict):
        error_and_exit(
            "Invalid data schema format. It must be a JSON object (dictionary).\n"
            "See --help for examples."
        )

    if not schema:
        error_and_exit("Data schema cannot be empty")

    for key, raw_value in schema.items():
        validate_schema_field(key, raw_value)

    return schema

def validate_schema_field(key: str, raw_value: str) -> None:
    if ":" not in raw_value:
        error_and_exit(
            f"Schema value for type of data '{raw_value}' must contain a colon (type:instruction). "
            "See --help for examples."
        )

    type_part, instruction = (part.strip() for part in raw_value.split(":", 1))

    validate_type_part(key, type_part, raw_value)
    validate_instruction_part(key, type_part, instruction, raw_value)


def validate_type_part(key: str, type_part: str, raw_value: str) -> None:
    if type_part not in VALID_DATA_TYPES:
        error_and_exit(
            f"Invalid type '{type_part}' in key '{key}' (value: '{raw_value}'). "
            f"Supported types: {', '.join(VALID_DATA_TYPES)}.\n"
            "Please check --help for the proper format."
        )

def validate_instruction_part(key: str, type_part: str, instruction_part: str, raw_value: str) -> None:
    if type_part == "timestamp":
        if instruction_part:
            error_and_exit(
                f"Key '{key}': timestamp type does not accept any instructions. "
                f"Value '{instruction_part}' which will be ignored."
            )
        return

    if instruction_part == "":
        return

    if instruction_part == "rand":
        validate_rand_instruction(key, type_part, raw_value)
        return

    if instruction_part.startswith("rand(") and instruction_part.endswith(")"):
        validate_rand_range_instruction(key, type_part, instruction_part, raw_value)
        return

    if instruction_part.startswith("[") and instruction_part.endswith("]"):
        validate_list_instruction(key, type_part, instruction_part)
        return

    validate_constant_instruction(key, type_part, instruction_part)


def validate_rand_instruction(key: str, type_part: str, raw_value: str) -> None:
    if type_part not in VALID_RAND_INSTRUCTION_DATA_TYPES:
        error_and_exit(
            f"'rand' instruction is only valid for str or int "
            f"(error in key '{key}', value '{raw_value}')."
        )

def validate_rand_range_instruction(key: str, type_part: str, instruction_part: str, raw_value: str) -> None:
    if type_part != "int":
        error_and_exit(
            f"rand(from, to) is only valid for int type "
            f"(error in key '{key}', value '{raw_value}')."
        )

    try:
        lower_str, upper_str = (s.strip() for s in instruction_part[5:-1].split(",", 1))
        lower_bound, upper_bound = int(lower_str), int(upper_str)

        if lower_bound > upper_bound:
            error_and_exit(
                f"Invalid range rand({lower_bound}, {upper_bound}) in key '{key}'. "
                "Lower bound must not exceed upper bound."
            )

    except (ValueError, IndexError):
        error_and_exit(
            f"Invalid format in rand(from, to) at key '{key}'. "
            "Example: int:rand(1, 90)"
        )

def validate_list_instruction(key: str, type_part: str, instruction_part: str) -> None:
    try:
        items = json.loads(instruction_part.replace("'", '"'))

        if not isinstance(items, list):
            error_and_exit(
                f"Instruction in key '{key}' must be a list when in [...] form."
            )

        if type_part == "str" and not all(isinstance(x, str) for x in items):
            error_and_exit(
                f"All elements in list for key '{key}' must be strings (type is str)."
            )

        if type_part == "int" and not all(isinstance(x, int) for x in items):
            error_and_exit(
                f"All elements in list for key '{key}' must be ints (type is int)."
            )

    except json.JSONDecodeError:
        error_and_exit(
            f"List instruction in key '{key}' must be valid JSON/array syntax."
        )

def validate_constant_instruction(key: str, type_part: str, instruction: str) -> None:
    if type_part == "str":
        if instruction == "rand":
            error_and_exit(
                f"Schema value for key '{key}' is invalid: '{instruction}'. "
                "It must contain a colon (type:instruction). "
                "See --help for examples."
            )
        return

    try:
        int(instruction)
    except ValueError:
        error_and_exit(
            f"Invalid format in key '{key}'. Expected format: type:instruction. "
            "See --help for examples."
        )