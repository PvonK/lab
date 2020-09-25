import argparse


def argument_definition():

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", type=int, default=5000,
                        help="port where server gets setup")

    parser.add_argument("-d", "--document-root",
                        help="root directory")

    parser.add_argument("-s", "--size", type=int, default=1024,
                        help="size of reading block")

    args = parser.parse_args()

    return args
