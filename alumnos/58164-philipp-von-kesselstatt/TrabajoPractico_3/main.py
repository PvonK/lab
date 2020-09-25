from argument_definition import argument_definition
from socketserver import ThreadingTCPServer
from handler import Handler
import os


def server_setup(port, directory, size):
    HOST, PORT = "localhost", port
    ThreadingTCPServer.allow_reuse_address = True
    with ThreadingTCPServer((HOST, PORT), Handler) as server:
        server.RequestHandlerClass.directory = directory
        server.RequestHandlerClass.size = size
        server.serve_forever()


def main():
    args = argument_definition()

    if not args.document_root:
        args.document_root = os.path.dirname(__file__) + "/images/"

    server_setup(args.port, args.document_root, args.size)


if __name__ == "__main__":
    main()
