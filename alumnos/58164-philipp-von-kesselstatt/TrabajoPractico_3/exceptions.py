from datetime import datetime
import os


class InternalServerError(Exception):
    def __init__(self, message):

        path = os.path.dirname(__file__)
        with open(path + "/log.txt", "a") as log:
            log.write("[{}][500 Internal Server Error] {}\n".format(
                    datetime.today().__str__()[:19],
                    message
                    )
                    )
        print(message)


class NotFoundError(Exception):
    def __init__(self, message):

        path = os.path.dirname(__file__)
        with open(path + "/log.txt", "a") as log:
            log.write("[{}][404 Not Found] {}\n".format(
                    datetime.today().__str__()[:19],
                    message
                    )
                    )
        print(message)
