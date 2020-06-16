class InvalidFormat(Exception):
    def __init__(self, message):
        print(message)


class NoFile(Exception):
    def __init__(self, message):
        print(message)


class OverflowError(Exception):
    def __init__(self, message):
        print(message)
