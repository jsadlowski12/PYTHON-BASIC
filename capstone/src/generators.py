import time
import uuid
import random
import json
import logging
from typing import Any
import os
import multiprocessing

from capstone.src.file_utils import clear_existing_files, print_data_to_console, save_data_to_file

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

def generate_file_name(file_name: str, file_prefix: str, index: int) -> str:
    if file_prefix == 'count':
        return f'{file_name}_{index}.json'
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

# Multiprocessing section for generation

def worker_generate_files(args: tuple) -> None:
    (file_indices, path_to_save_files, file_name, file_prefix,
     data_lines, data_schema, files_count) = args

    for i in file_indices:
        data = generate_data_lines(data_schema, data_lines)

        filename = generate_file_name(file_name, file_prefix, i)
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