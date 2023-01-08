import ast
import astor
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
    with open(filename, "r", encoding='utf-8') as f:
        return f.read()


def get_read_pointer(filename):
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

# 0.9765828274067649
class Tree:
    def __init__(self, code):
        self.parsed = ast.parse(code)
        self.variables = []

    def delete_docstring(self):
        for node in ast.walk(self.parsed):
            if isinstance(node, ast.Name):
                node.id = node.id.lower().replace('_', '')

            if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                continue

            if not len(node.body):
                continue

            if not isinstance(node.body[0], ast.Expr):
                continue

            if not hasattr(node.body[0], 'value') or not isinstance(node.body[0].value, ast.Str):
                continue

            node.body = node.body[1:]
        return self.parsed

    def get_code_syntax_tree(self) -> str:
        parsed = self.delete_docstring()

        normalized_code = ast.dump(parsed, annotate_fields=True)
        print(normalized_code)
        return astor.to_source(parsed)


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

                code_orig = Tree(read(filenames[0])).get_code_syntax_tree()
                code_copy = Tree(read(filenames[1])).get_code_syntax_tree()

                distance = self.levenstein(code_orig, code_copy)

                similarity = 1 - (distance / len(code_orig))
                w.write(str(similarity) + '\n')

    @staticmethod
    def levenstein(str_1: str, str_2: str) -> int:
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
    apg = Antiplagiarism(Parser())
    apg.handle_files()


if __name__ == "__main__":
    main()
