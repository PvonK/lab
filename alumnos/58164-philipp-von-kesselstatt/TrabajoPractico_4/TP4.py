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


async def handler(reader, writer):
    path = os.path.dirname(__file__) + "/"
    address = writer.get_extra_info('peername')
    asyncio.create_task(log_user(path, address[0], address[1]))

    recieved = (await reader.read(args.size)).decode()

    if "GET" in recieved:
        request = recieved.split()[1]
        try:
            if request == "/":

                index = ls_html(path)
                writer.write(index)
                await writer.drain()
                writer.close()
                await writer.wait_closed()

            elif os.path.isdir(request):

                index = ls_html(request)
                writer.write(index)
                await writer.drain()
                writer.close()
                await writer.wait_closed()

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

            else:

                header = create_http_header(path + "html/404.html")
                writer.write(header)
                fd = os.open(path + "html/404.html", os.O_RDONLY)
                while True:
                    body = os.read(fd, args.size)
                    writer.write(body)
                    if(len(body) != args.size):
                        break
                await writer.drain()
                writer.close()
                await writer.wait_closed()
        except:
            header = create_http_header(path + "html/500.html")
            writer.write(header)
            fd = os.open(path + "html/500.html", os.O_RDONLY)
            while True:
                body = os.read(fd, args.size)
                writer.write(body)
                if(len(body) != args.size):
                    break
            await writer.drain()
            writer.close()
            await writer.wait_closed()


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

    asyncio.run(server(["127.0.0.1", "::1"], args.port))
