import asyncio
import socket
import datetime
import os

from argument_definition import argument_definition
from html_creator import ls_html


async def log_user(path, adress, port):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = "cliente: {}:{}, tiempo: {}\n".format(adress, port, time)

    with open(path + "log.txt", "a") as f:
        f.write(log)


async def debug_file(path, req, func):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = "Fecha: {}\n".format(time)
    log += "Request: {}\n".format(req)
    log += "Funciones:\n{}\n".format(func)
    log += "-"*140
    log += "\n\n"

    with open(path + "debug.txt", "a") as f:
        f.write(log)


async def handler(reader, writer):
    path = os.getcwd() + "/"
    address = writer.get_extra_info('peername')
    asyncio.create_task(log_user(path, address[0], address[1]))

    recieved = (await reader.read(args.size)).decode()

    if "GET" in recieved:
        request = recieved.split()[1]
        try:
            if request == "/":

                index = ls_html(args.document_root)
                writer.write(index)
                await writer.drain()
                writer.close()
                await writer.wait_closed()

                funciones = """\tls_html({})
                               """.format(args.document_root, index)

            elif os.path.isdir(request):

                index = ls_html(request)
                writer.write(index)
                await writer.drain()
                writer.close()
                await writer.wait_closed()

                funciones = """\tls_html({})
                               """.format(request, index)

            elif os.path.isfile(request):
                header = create_http_header(request)
                writer.write(header)
                fd = os.open(request, os.O_RDONLY)
                while True:
                    body = os.read(fd, args.size)
                    writer.write(body)
                    if(len(body) != args.size):
                        break
                await writer.drain()
                writer.close()
                await writer.wait_closed()

                funciones = "\tcreate_http_header({})\n".format(request) + \
                            "\tos.open({}, os.O_RDONLY)\n".format(request) + \
                            "\tos.read({}, args.size)\n".format(fd)

                os.close(fd)

            else:
                err = path + "html/404.html"
                header = create_http_header(err)
                writer.write(header)
                fd = os.open(err, os.O_RDONLY)
                while True:
                    body = os.read(fd, args.size)
                    writer.write(body)
                    if(len(body) != args.size):
                        break
                await writer.drain()
                writer.close()
                await writer.wait_closed()

                funciones = "\tcreate_http_header({})\n".format(request) + \
                            "\tos.open({}, os.O_RDONLY)\n".format(request) + \
                            "\tos.read({}, args.size)\n".format(fd)

                os.close(fd)

        except Exception:
            err = path + "html/500.html"
            header = create_http_header(err)
            writer.write(header)
            fd = os.open(err, os.O_RDONLY)
            while True:
                body = os.read(fd, args.size)
                writer.write(body)
                if(len(body) != args.size):
                    break
            await writer.drain()
            writer.close()
            await writer.wait_closed()

            funciones = "\tcreate_http_header({})\n".format(request) + \
                        "\tos.open({}, os.O_RDONLY)\n".format(request) + \
                        "\tos.read({}, args.size)\n".format(fd)

            os.close(fd)

        if args.debug:
            asyncio.create_task(debug_file(path, request, funciones))


def create_http_header(page):

    file_size = os.path.getsize(page)

    contentType = {
                    ".html": b"text/html",
                    ".jpg": b"image",
                    ".jpeg": b"image",
                    ".png": b"image",
                    ".pdf": b"application/pdf",
                    ".mp3": b"audio/mpeg",
                    }

    extension = page[page.find("."):]

    try:
        typ = contentType[extension]
    except KeyError:
        typ = b"*/*"

    http_header = b"HTTP/1.1 200 OK\nContent-Type: "
    http_header += typ + b"\nContent-Length: "
    http_header += str(file_size).encode()
    http_header += b"\n\n"

    return http_header


async def server(host, port):
    server = await asyncio.start_server(
                                        handler,
                                        host,
                                        port,
                                        family=socket.AF_UNSPEC
                                        )
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    path = os.path.dirname(__file__) + "/"
    args = argument_definition()

    asyncio.run(server(["172.17.0.2"], args.port))
