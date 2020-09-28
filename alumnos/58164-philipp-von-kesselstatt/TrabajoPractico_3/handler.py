from socketserver import BaseRequestHandler
import os
import thread_work
import concurrent.futures as fut
from header_parser import readHeader, createHeader
from html_creator import HtmlCreator
from exceptions import InternalServerError, NotFoundError
# toDo: Poner explicaciones en comentarios


class Handler(BaseRequestHandler):

    def handle(self):

        enviado = self.request.recv(1024).strip()
        print(enviado.decode() + "\n\n")
        self.requestParser(enviado)

    def requestParser(self, req):

        if req.startswith(b"GET"):
            self.processGetRequest(req)
        elif req.startswith(b"HEAD"):
            pass
        elif req.startswith(b"POST"):
            pass
        elif req.startswith(b"PUT"):
            pass
        elif req.startswith(b"DELETE"):
            pass
        elif req.startswith(b"CONNECT"):
            pass
        elif req.startswith(b"OPTIONS"):
            pass
        elif req.startswith(b"TRACE"):
            pass
        else:
            self.request.sendall(b"HTTP not recognized")

    def processGetRequest(self, req):

        req = req.splitlines()
        page = req[0].split()[1].decode()
        page = page.replace("%20", " ")

        if os.path.isfile(page):
            self.open_file(page)

        elif page.find("?") != -1:
            self.read_arguments(page)

        elif os.path.isdir(page):
            if page == "/":
                self.ls_html(self.directory)
            else:
                self.ls_html(page)

        else:
            self.notFound(page)

    def ls_html(self, page):

        if not page.endswith("/"):
            page += "/"
        folderNameIndex = page.rfind("/", 0, -1)
        folderName = page[folderNameIndex:]

        h = HtmlCreator()
        h.title(h.centerText(folderName), 3)

        files = os.listdir(page)
        for data in files:

            if data.endswith(".ppm"):
                h.createRadioInput("R", "filter", "R", "Red")
                h.createRadioInput("G", "filter", "G", "Green")
                h.createRadioInput("B", "filter", "B", "Blue")
                h.createRadioInput("W", "filter", "W", "Black & White")

                h.createTextInput("number", "Scale:", "scale", "scale",
                                  minimum=0, step=0.01)

                h.createForm(page + data, data, False)

            else:
                h.createHiperlink(page + data, data)
                h.addLine()

        html_code = h.getHtml().encode()
        http_header = b"HTTP/1.1 200 OK\nContent-Type: text/html\nContent-"
        http_header += b"Length: " + str(len(html_code)).encode() + b"\n\n"
        self.request.sendall(http_header + html_code)

    def notFound(self, message):
        http_header = b"HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n"
        self.request.sendall(http_header)
        fd = os.open(os.path.dirname(__file__) + "/html/404.html", os.O_RDONLY)
        self.read_and_send(fd, round(170/self.size+0.5))

        raise NotFoundError(message)

        # http_header = b"HTTP/1.1 200 OK\nContent-Type: */*\n\n"
        # self.request.sendall(http_header)
        # self.open_file("/home/philipp/Git/compu2/lab/alumnos/58164-philipp-von-kesselstatt/TrabajoPractico_3/images/7o.ppm")
        # ^ sirve para ver navegador le pone nombre al archivo a descargar

    def read_arguments(self, page):
        delimiter = page.find("?")

        if os.path.isdir(page[:delimiter]):
            message = "Cant put arguments on that page ({})".format(page)
            self.internalServerError(message)

        arguments = page[delimiter+1:]

        arguments = arguments.split("&")

        if len(arguments) == 2:
            filtro = arguments[0][arguments[0].find("=")+1:]
            try:
                scale = float(arguments[1][arguments[1].find("=")+1:])
            except ValueError:
                message = "' {} ' is not a valid scale value"\
                    .format(arguments[1][arguments[1].find("=")+1:])
                self.internalServerError(message)

            param = (filtro, scale)
        else:
            param = ()

        page = page[:delimiter]

        if not page.endswith(".ppm"):
            self.internalServerError("Can't put filter on {}".format(page))
        self.open_file(page, *param)

    def open_file(self, page, *arguments):

        self.size = self.size - (self.size % 3)

        file_size = os.path.getsize(page)
        number_of_blocks = round(file_size/self.size+0.5)

        fd = os.open(page, os.O_RDONLY)

        if not arguments:

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

            self.request.sendall(http_header)
            self.read_and_send(fd, number_of_blocks)

        else:

            filtro, scale = arguments
            self.color_filter(
                              filtro,
                              scale,
                              fd,
                              number_of_blocks,
                              file_size
                              )

        os.close(fd)

    def read_and_send(self, fd, number_of_blocks):
        for i in range(number_of_blocks):
            file_block = os.read(fd, self.size)
            self.request.sendall(file_block)

    def color_filter(self,
                     filtro,
                     scale,
                     fd,
                     number_of_blocks,
                     file_size):

        filters = {
                   "W": thread_work.thread_black_white,
                   "R": thread_work.thread_red_filter,
                   "G": thread_work.thread_green_filter,
                   "B": thread_work.thread_blue_filter
                   }

        try:
            func = filters[filtro]
        except KeyError:
            self.internalServerError(
                                    "Filter '{}' not supported".format(filtro)
                                     )

        hilos = fut.ThreadPoolExecutor()

        array_list = []

        header_end, width, height, max_v, comments = readHeader(fd)
        ppm_header = createHeader(width, height, max_v)

        http_header = b"HTTP/1.1 200 OK\nContent-Type: */*\n"
        http_header += "Content-Length: {}\n\n".format(
                                file_size - header_end + len(ppm_header)
                                ).encode()

        self.request.sendall(http_header + ppm_header.encode())

        os.lseek(fd, header_end, 0)
        for i in range(number_of_blocks):
            file_block = os.read(fd, self.size)
            array_list.append(
                              hilos.submit(func,
                                           file_block,
                                           scale,
                                           max_v
                                           )
                              )

        for ar in array_list:
            self.request.sendall(ar.result())

    def internalServerError(self, message):

        h = HtmlCreator()
        h.title(h.centerText("500 Internal Server Error"), 1)
        h.title(h.centerText(message), 3)

        code = h.getHtml().encode()

        http_header = b"HTTP/1.1 500 Internal Server Error\n"
        http_header += b"Content-Type: text/html\n"
        http_header += "Content-Length: {}\n\n".format(len(code)).encode()

        self.request.sendall(http_header + code)

        raise InternalServerError(message)
