import argparse
import logging
import sys
import os
import configparser
import random
import uuid
import json
from typing import Any

VALID_DATA_TYPES = {'str', 'int', 'timestamp'}

def create_parser() -> argparse.ArgumentParser:
    defaults = load_defaults_from_config()

    parser = argparse.ArgumentParser(prog='magicgenerator',
                            description='A console utility for generating test data based on data schema',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--path_to_save_files',
                        default=defaults['path_to_save_files'],
                        help='Path to where the files are saved.')
    parser.add_argument('--files_count',
                        default=defaults['files_count'],
                        type=int,
                        help='How many JSON files to generate. '
                        'Count must be greater or equal to 0. If equal to 0 the output will be printed to console.')
    parser.add_argument('--file_name',
                        default=defaults['file_name'],
                        help='Base file_name. If there is no prefix, the final file name will be file_name.json. '
                             'With prefix full file name will be file_name_file_prefix.json')
    parser.add_argument('--file_prefix',
                        default=defaults['file_prefix'],
                        choices=['count', 'random', 'uuid'],
                        help='What prefix for file name to use if more than 1 file needs to be generated')
    parser.add_argument('--data_schema',
                        required=True,
                        type=str,
                        help=(
                            "JSON schema as a string. Can be provided in two ways:\n"
                            "1) Path to a JSON file: e.g., './schema.json'\n"
                            "2) Inline JSON string: e.g., "
                            "'{\"name\": \"str:rand\", \"age\": \"int:rand(1, 100)\", \"type\": \"str:['client','partner']\"}'\n\n"
                            "All values must follow the pattern type:instruction.\n"
                            "Supported types: str, int, timestamp.\n"
                            "Instructions include: rand, rand(from, to), list values, fixed value, or empty.\n")
                        )
    parser.add_argument('--data_lines',
                        default=defaults['data_lines'],
                        type=int,
                        help='Count of lines for each file. Default: 1000.')
    parser.add_argument('--clear_path',
                        default=defaults['clear_path'],
                        action='store_true',
                        help='If this flag is on, before the script starts creating new data files, '
                             'all files in path_to_save_files that match file_name will be deleted.')
    parser.add_argument('--multiprocessing',
                        default=defaults['multiprocessing'],
                        type=int,
                        help='The number of processes used to create files. '
                             'Divides the “files_count” value equally and starts N processes '
                             'to create an equal number of files in parallel.')

    return parser

def load_defaults_from_config(config_file='default.ini'):
    if not os.path.exists(config_file):
        logging.error(f"Required configuration file '{config_file}' not found.")
        sys.exit(1)

    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        logging.info(f"Default configuration successfully loaded from '{config_file}'")

        path_to_save_files = config.get('DEFAULT', 'path_to_save_files')
        logging.info(f"Loaded path_to_save_files: {path_to_save_files}")

        files_count = config.getint('DEFAULT', 'files_count')
        logging.info(f"Loaded files_count: {files_count}")

        file_name = config.get('DEFAULT', 'file_name')
        logging.info(f"Loaded file_name: {file_name}")

        file_prefix = config.get('DEFAULT', 'file_prefix')
        logging.info(f"Loaded file_prefix: {file_prefix}")

        data_lines = config.getint('DEFAULT', 'data_lines')
        logging.info(f"Loaded data_lines: {data_lines}")

        clear_path = config.getboolean('DEFAULT', 'clear_path')
        logging.info(f"Loaded clear_path: {clear_path}")

        multiprocessing = config.getint('DEFAULT', 'multiprocessing')
        logging.info(f"Loaded multiprocessing: {multiprocessing}")

        return {
            'path_to_save_files': path_to_save_files,
            'files_count': files_count,
            'file_name': file_name,
            'file_prefix': file_prefix,
            'data_lines': data_lines,
            'clear_path': clear_path,
            'multiprocessing': multiprocessing
        }

    except (configparser.Error, ValueError, KeyError) as e:
        logging.error(f"Invalid configuration in '{config_file}': {e}")
        sys.exit(1)

def validate_path_to_save_files(path_input: str) -> str:
    if path_input == '.':
        return os.getcwd()

    if os.path.isabs(path_input):
        absolute_path = path_input
    else:
        absolute_path = os.path.abspath(path_input)

    if not os.path.exists(absolute_path):
        logging.error(f"Path does not exist: {absolute_path}")
        sys.exit(1)

    if not os.path.isdir(absolute_path):
        logging.error(f"Path exists but is not a directory: {absolute_path}")
        sys.exit(1)

    if not os.access(absolute_path, os.W_OK):
        logging.error(f"No write permission for directory: {absolute_path}")
        sys.exit(1)

    return absolute_path

def validate_files_count(files_count: int) -> int:
    if files_count < 0:
        logging.error(f"files_count can't be a negative number: {files_count}. "
                      f"Check --help for more information about expected value.")
        sys.exit(1)

    return files_count

def validate_data_lines(data_lines: int) -> int:
    if data_lines <= 0:
        logging.error(f"data_lines argument can't be a negative number or zero: {data_lines}")
        sys.exit(1)

    return data_lines

def validate_multiprocessing(multiprocessing: int) -> int:
    if multiprocessing < 0:
        logging.error(f"multiprocessing argument can't be a negative number: {multiprocessing}")
        sys.exit(1)

    cpu_count = os.cpu_count()
    if multiprocessing > cpu_count:
        logging.warning(f"multiprocessing argument value {multiprocessing} is greater than CPU count {cpu_count}, "
                        f"using {cpu_count} instead")
        return cpu_count

    return multiprocessing

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
        logging.error(
            "Invalid data schema format. The schema must be a JSON object (dictionary).\n"
            "Please check --help for examples and format instructions."
        )
        sys.exit(1)

    if not schema:
        logging.error("Data schema cannot be empty")
        sys.exit(1)

    validate_schema_types(schema)

    parsed_schema = {}
    return parsed_schema

def validate_schema_types(schema: dict[str, str]) -> None:
    for key, value in schema.items():
        if ':' not in value:
            logging.error(
                f"Schema value for key '{key}' must contain a colon (type:instruction). "
                "See --help for examples."
            )
            sys.exit(1)

        parts = value.split(':', 1)
        if len(parts) != 2:
            logging.error(
                f"Invalid format in key '{key}'. Expected format: type:instruction. "
                "See --help for examples."
            )
            sys.exit(1)

        type_hint = parts[0].strip()
        instruction = parts[1].strip()

        if type_hint not in VALID_DATA_TYPES:
            logging.error(
                f"Invalid type '{type_hint}' in schema key '{key}'. "
                f"Supported types are: {', '.join(VALID_DATA_TYPES)}.\n"
                "Please check --help for proper schema format.\n"
            )
            sys.exit(1)

def generate_file_name(file_name: str, file_prefix: str, files_count: int, index: int) -> str:
    if files_count == 1:
        return f'{file_name}.json'
    elif file_prefix == 'count':
        return f'{file_name}_{index}'
    elif file_prefix == 'random':
        return f"{file_name}_{random.randint(1000, 9999)}.json"
    elif file_prefix == 'uuid':
        return f"{file_name}_{uuid.uuid4()}.json"
    else:
        return f"{file_name}_{index}.json"

def validate_all_arguments(args: argparse.Namespace) -> dict:
    validated_path = validate_path_to_save_files(args.path_to_save_files)
    logging.info(f"Provided path argument: {validated_path} is valid.")

    validated_files_count = validate_files_count(args.files_count)
    logging.info(f"Provided files_count argument: {validated_files_count} is valid.")

    validated_data_lines = validate_data_lines(args.data_lines)
    logging.info(f"Provided data_lines argument: {validated_data_lines} is valid.")

    validated_data_schema = validate_data_schema(args.data_schema)
    logging.info(f"Provided data_schema argument: {validated_data_lines} is valid.")

    validated_multiprocessing = validate_multiprocessing(args.multiprocessing)
    logging.info(f"Provided multiprocessing argument: {validated_multiprocessing} is valid.")

    return {'path_to_save_files': validated_path,
            'file_name': args.file_name,
            'file_prefix': args.file_prefix,
            'files_count': validated_files_count,
            'data_lines': validated_data_lines,
            'data_schema': validated_data_schema,
            'clear_path': args.clear_path,
            'multiprocessing': validated_multiprocessing
            }

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    parser = create_parser()
    args = parser.parse_args()

    validated_args = validate_all_arguments(args)

    logging.debug(load_json_data_schema(validated_args['data_schema']))

    logging.info(f"Files will be saved to: {validated_args['path_to_save_files']}")
    logging.info(f"There will be {validated_args['files_count']} files created.")
    logging.info(f"There will be {validated_args['data_lines']} lines in file created.")
    logging.info(f"There will be {validated_args['multiprocessing']} processes created.")

if __name__ == "__main__":
    main()