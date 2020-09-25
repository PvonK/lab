from socketserver import BaseRequestHandler
import os
import thread_work
import concurrent.futures as fut
from header_parser import readHeader, createHeader
from html_creator import HtmlCreator


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
            self.notfound()

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

                h.createTextInput("Scale:", "scale", "scale", 1)

                h.createForm(page + data, data, False)

            else:
                h.createHiperlink(page + data, data)
                h.addLine()

        htmlCode = h.getHtml().encode()
        header = b"HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: "
        header += str(len(htmlCode)).encode() + b"\n\n"
        self.request.sendall(header + htmlCode)

    def notfound(self):
        header = b"HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n"
        self.request.sendall(header)
        self.open_file(os.path.dirname(__file__) + "/html/404.html")

        # header = b"HTTP/1.1 200 OK\nContent-Type: */*\n\n"
        # self.request.sendall(header)
        # self.open_file("/home/philipp/Git/compu2/lab/alumnos/58164-philipp-von-kesselstatt/TrabajoPractico_3/images/7o.ppm")

    def read_arguments(self, page):
        delimiter = page.find("?")
        arguments = page[delimiter+1:]

        arguments = arguments.split("&")

        if len(arguments) == 2:
            filtro = arguments[0][arguments[0].find("=")+1:]
            scale = arguments[1][arguments[1].find("=")+1:]
            param = (filtro, float(scale))
        else:
            param = ()

        self.open_file(page[:delimiter], *param)

    def open_file(self, page, *arguments):

        self.size = self.size - (self.size % 3)

        file_size = os.path.getsize(page)
        number_of_blocks = round(file_size/self.size+0.5)

        fd = os.open(page, os.O_RDONLY)

        if not arguments:
            self.contentType = {".html": b"text/html",
                                ".jpg": b"image",
                                ".jpeg": b"image",
                                ".png": b"image",
                                ".pdf": b"application/pdf",
                                ".mp3": b"audio/mpeg",
                                }
            extension = page[page.find("."):]

            try:
                typ = self.contentType[extension]
            except KeyError:
                typ = b"*/*"

            header = b"HTTP/1.1 200 OK\nContent-Type: "
            header += typ + b"\nContent-Length: " + str(file_size).encode()
            header += b"\n\n"

            self.request.sendall(header)
            self.read_and_send(fd, number_of_blocks)

        else:

            filtro, scale = arguments
            self.color_filter(filtro,
                              scale,
                              fd,
                              number_of_blocks,
                              file_size)

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

        hilos = fut.ThreadPoolExecutor()

        array_list = []

        if filtro == "W":
            func = thread_work.thread_black_white
        elif filtro == "R":
            func = thread_work.thread_red_filter
        elif filtro == "G":
            func = thread_work.thread_green_filter
        elif filtro == "B":
            func = thread_work.thread_blue_filter
        else:
            raise Exception  # toDo: crear excepcion para filtros mal

        header_end, width, height, max_v, comments = readHeader(fd)
        new_header = createHeader(width, height, max_v)

        os.lseek(fd, header_end, 0)
        for i in range(number_of_blocks):
            file_block = [i for i in os.read(fd, self.size)]
            array_list.append(hilos.submit(func,
                                           file_block, file_size, scale, max_v)
                              )

        a = b""
        for ar in array_list:
            a += ar.result()

        header = b"HTTP/1.1 200 OK\nContent-Type: */*\n\n"

        self.request.sendall(header)
        self.request.sendall(new_header.encode() + a)
