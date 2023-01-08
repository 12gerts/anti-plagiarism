import ast
import argparse
import os
import sys


def is_exist(path):
    """ Checking the existence of a file or directory. """
    if not os.path.exists(path):
        print('[ERROR] a directory or file that does not exist')
        sys.exit()
    else:
        return path


def read(filename):
    """ Gives data from a file. """
    with open(filename, "r", encoding='utf-8') as f:
        return f.read()


def get_read_pointer(filename):
    """ Gives a pointer to read the file """
    return open(filename, "r", encoding='utf-8')


class Parser:
    def __init__(self):
        self.input, self.output = self.parse()

    @staticmethod
    def parse():
        """ Parsing command line arguments. """
        parser = argparse.ArgumentParser()

        parser.add_argument('input',
                            type=str,
                            help='Enter the input file')
        parser.add_argument('output',
                            type=str,
                            help='Enter the output file')

        arguments = parser.parse_args()
        return is_exist(arguments.input), arguments.output


class Tree:
    def __init__(self, filenames):
        self.parsed = [ast.parse(read(filenames[0])), ast.parse(read(filenames[1]))]
        self.mode = 0
        self.variables = []

    def delete_doc_and_rename_vars(self) -> ast:
        """ Remove comments, docstrings and rename variables when similar. """
        iterator = 0
        for node in ast.walk(self.parsed[self.mode]):
            if isinstance(node, ast.Name):
                node.id = node.id.lower().replace('_', '')
                if self.mode == 0:
                    self.variables.append(node.id)
                if self.mode == 1 and iterator != len(self.variables):
                    if node.id.startswith(self.variables[iterator]) or self.variables[iterator].startswith(node.id):
                        node.id = self.variables[iterator]
                    elif levenstein(node.id, self.variables[iterator]) == 1:
                        node.id = self.variables[iterator]
                    iterator += 1

            if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                continue

            if not len(node.body):
                continue

            if not isinstance(node.body[0], ast.Expr):
                continue

            if not hasattr(node.body[0], 'value') or not isinstance(node.body[0].value, ast.Str):
                continue

            node.body = node.body[1:]
        return self.parsed[self.mode]

    def code_preprocessing(self) -> str:
        """ Preprocess the tree and return the code. """
        parsed = self.delete_doc_and_rename_vars()
        return ast.unparse(parsed)


class Antiplagiarism:
    def __init__(self, parser):
        self.input_list = parser.input
        self.output = parser.output

    def handle_files(self):
        with open(self.output, "w") as w:
            for line in get_read_pointer(self.input_list):
                filenames = line.strip().split()

                for file in filenames:
                    is_exist(file)

                tree = Tree(filenames)
                code_orig = tree.code_preprocessing()
                tree.mode = 1
                code_copy = tree.code_preprocessing()

                distance = levenstein(code_orig, code_copy)

                similarity = 1 - (distance / len(code_orig))
                w.write(f'{round(similarity, 3)}\n')


def levenstein(str_1: str, str_2: str) -> int:
    """ Count the Levenshtein distance. """
    if str_1 == str_2:
        return 0

    n, m = len(str_1), len(str_2)
    if n > m:
        str_1, str_2 = str_2, str_1
        n, m = m, n

    current_row = range(n + 1)

    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n

        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]

            if str_1[j - 1] != str_2[i - 1]:
                change += 1

            current_row[j] = min(add, delete, change)

    return current_row[n]


def main():
    antiplagiarism = Antiplagiarism(Parser())
    antiplagiarism.handle_files()


if __name__ == "__main__":
    main()
