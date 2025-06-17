"""
Read files from ./files and extract values from them.
Write one file with all values separated by commas.

Example:
    Input:

    file_1.txt (content: "23")
    file_2.txt (content: "78")
    file_3.txt (content: "3")

    Output:

    result.txt(content: "23, 78, 3")
"""
from fileinput import filename
import os

def read_files(file_paths: list[str]):
    result = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as content:
                result.append(content.read())
        except FileNotFoundError:
            print(f"Missing file: {file_path}")
    return result

def write_to_file(filename: str, content: list[str]):
    with open(filename, 'w') as file:
        file.write(','.join(map(str, content)))

if __name__ == "__main__":
    folder_path = './files'

    files = os.listdir(folder_path)

    file_paths = [os.path.join(folder_path, file)
                  for file in files if os.path.isfile(os.path.join(folder_path, file))]

    content = read_files(file_paths)
    write_to_file("result.txt", content)