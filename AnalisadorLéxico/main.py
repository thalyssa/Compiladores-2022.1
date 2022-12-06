import argparse
from os.path import isfile, splitext
import lexer


def process_file(path):
    token = lexer.Lexer(path)

    while not token.is_EOF():
        next_token = token.next_token()
        print(next_token)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Validation for files written in Neon language')
    arg_parser.add_argument('Path', metavar='path', type=str, help='Path to .nbl file')

    args = arg_parser.parse_args()
    input_path = args.Path

    if not isfile(input_path):
        print('Invalid file path.')
        exit()
    elif splitext(input_path)[1] != '.nbl':
        print('Invalid file extension.')
        exit()

    process_file(input_path)
