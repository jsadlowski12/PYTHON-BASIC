import argparse
import logging
import sys
import os
import random
import uuid
import json
import time
import glob
import multiprocessing
from typing import Any

from capstone.src.config_loader import load_defaults_from_config
from capstone.src.arguments_validators import validate_all_arguments

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


def generate_value(type_part: str, instruction_part: str) -> Any:
    if type_part == "timestamp":
        return time.time()

    if instruction_part == "":
        return "" if type_part == "str" else None

    if instruction_part == "rand":
        return str(uuid.uuid4()) if type_part == "str" else random.randint(0, 10000)

    if instruction_part.startswith("rand(") and instruction_part.endswith(")"):
        lower_str, upper_str = (s.strip() for s in instruction_part[5:-1].split(",", 1))
        lower_bound, higher_bound = int(lower_str), int(upper_str)
        return random.randint(lower_bound, higher_bound)

    if instruction_part.startswith("[") and instruction_part.endswith("]"):
        items = json.loads(instruction_part.replace("'", '"'))
        return random.choice(items)

    return instruction_part if type_part == "str" else int(instruction_part)

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

def generate_data_record(data_schema: dict[str, str]) -> dict:
    record = {}
    for key, raw_value in data_schema.items():
        type_part, instruction_part = (part.strip() for part in raw_value.split(":", 1))
        record[key] = generate_value(type_part, instruction_part)
    return record

def generate_data_lines(data_schema: dict[str, str], data_lines: int) -> list[dict]:
    return [generate_data_record(data_schema) for _ in range(data_lines)]

def clear_existing_files(path_to_save_files: str, file_name: str) -> None:
    pattern = os.path.join(path_to_save_files, f"{file_name}*.json")
    existing_files = glob.glob(pattern)

    if existing_files:
        logging.info(f"Clearing {len(existing_files)} existing files matching pattern: {file_name}*.json")
        for file_path in existing_files:
            try:
                os.remove(file_path)
                logging.debug(f"Deleted file: {file_path}")
            except OSError as e:
                logging.error(f"Failed to delete file {file_path}: {e}")
                sys.exit(1)
        logging.info(f"Successfully cleared {len(existing_files)} existing files")
    else:
        logging.info(f"No existing files found matching pattern: {file_name}*.json")


def print_data_to_console(data: list[dict]) -> None:
    try:
        for record in data:
            print(json.dumps(record, indent=2))
    except (TypeError, ValueError) as e:
        logging.error(f"Error printing data to console: {e}")
        sys.exit(1)


def save_data_to_file(data: list[dict], file_path: str) -> None:
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Successfully saved {len(data)} records to: {file_path}")
    except (OSError, TypeError, ValueError) as e:
        logging.error(f"Error saving data to file {file_path}: {e}")
        sys.exit(1)

def worker_generate_files(args: tuple) -> None:
    (file_indices, path_to_save_files, file_name, file_prefix,
     data_lines, data_schema, files_count) = args

    for i in file_indices:
        data = generate_data_lines(data_schema, data_lines)

        filename = generate_file_name(file_name, file_prefix, files_count, i)
        file_path = os.path.join(path_to_save_files, filename)

        save_data_to_file(data, file_path)

def distribute_files_across_processes(files_count: int, process_count: int) -> list[list[int]]:
    files_per_process = files_count // process_count
    remainder = files_count % process_count

    file_distribution = []
    current_index = 1

    for i in range(process_count):
        files_for_this_process = files_per_process + (1 if i < remainder else 0)

        if files_for_this_process > 0:
            file_indices = list(range(current_index, current_index + files_for_this_process))
            file_distribution.append(file_indices)
            current_index += files_for_this_process
        else:
            file_distribution.append([])

    return file_distribution

def generate_and_save_data(args: dict) -> None:
    if args['clear_path']:
        clear_existing_files(args['path_to_save_files'], args['file_name'])

    if args['files_count'] == 0:
        logging.info("Printing generated data to console (files_count = 0)")
        data = generate_data_lines(args['data_schema'], args['data_lines'])
        print_data_to_console(data)
        return

    if args['multiprocessing'] <= 1:
        logging.info("Using single process for file generation")
        for i in range(1, args['files_count'] + 1):
            data = generate_data_lines(args['data_schema'], args['data_lines'])
            filename = generate_file_name(
                args['file_name'],
                args['file_prefix'],
                args['files_count'],
                i
            )
            file_path = os.path.join(args['path_to_save_files'], filename)
            save_data_to_file(data, file_path)
        return

    logging.info(f"Using {args['multiprocessing']} processes for file generation")

    file_distribution = distribute_files_across_processes(args['files_count'], args['multiprocessing'])

    worker_args = []
    for file_indices in file_distribution:
        if file_indices:
            worker_args.append((
                file_indices,
                args['path_to_save_files'],
                args['file_name'],
                args['file_prefix'],
                args['data_lines'],
                args['data_schema'],
                args['files_count']
            ))

    if worker_args:
        with multiprocessing.Pool(processes=len(worker_args)) as pool:
            pool.map(worker_generate_files, worker_args)
            pool.close()
            pool.join()

    logging.info(f"Successfully generated {args['files_count']} files using {len(worker_args)} processes")

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

    parser = create_parser()
    args = parser.parse_args()
    validated_args = validate_all_arguments(args)
    generate_and_save_data(validated_args)

if __name__ == "__main__":
    main()