import argparse
import sys
from argparse import ArgumentParser


def create_parser():
    parser = ArgumentParser(prog='magicgenerator',
                            description='A console utility for generating test data based on data schema',
                            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--path_to_save_files', help='Path to where the files are saved.')
    parser.add_argument('--files_count', type=int, help='How many JSON files to generate')
    parser.add_argument('--file_name',
                        help='Base file_name. If there is no prefix, the final file name will be file_name.json. '
                             'With prefix full file name will be file_name_file_prefix.json')
    parser.add_argument('--file_prefix', choices=['count', 'random', 'uuid'],
                        help='What prefix for file name to use if more than 1 file needs to be generated')
    parser.add_argument('--data_schema', required=True, type=str,
                        help='It’s a string with json schema. '
                             'It could be loaded in two ways: '
                            '1) With path to json file with schema 2) with schema entered to command line.')
    parser.add_argument('--data_lines', type=int,
                        help='Count of lines for each file. Default, for example: 1000.')
    parser.add_argument('--clear_path', action='store_true',
                        help='If this flag is on, before the script starts creating new data files, '
                             'all files in path_to_save_files that match file_name will be deleted.')
    parser.add_argument('--multiprocessing', type=int,
                        help='The number of processes used to create files. '
                             'Divides the “files_count” value equally and starts N processes '
                             'to create an equal number of files in parallel.')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

if __name__ == "__main__":
    main()