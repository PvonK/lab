import argparse


def argument_definition():

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", type=int, default=5000,
                        help="port where server gets setup")

    parser.add_argument("-r", "--document_root", default="/",
                        help="root directory")

    parser.add_argument("-s", "--size", type=int, default=1024,
                        help="size of reading block")

    parser.add_argument("-d", "--debug", action="store_true",
                        help="creates debug file")

    args = parser.parse_args()

    return args
