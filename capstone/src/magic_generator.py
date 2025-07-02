import argparse
import sys
from argparse import ArgumentParser


def create_parser():
    parser = ArgumentParser(prog='magicgenerator',
                            description='A console utility for generating test data based on data schema')

    parser.add_argument('path_to_save_files', help='Path to where the files are saved.')
    parser.add_argument('--files_count', type=int, help='How many JSON files to generate')
    parser.add_argument('--file_name')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

if __name__ == "__main__":
    main()