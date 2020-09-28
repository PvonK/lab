import os


def readHeader(fd):
    lines = os.read(fd, 100).splitlines()
    comments = []
    header_end = 0
    for line in lines:
        if line == b"P6":
            header_end += len(line) + 1
        elif line[0] == ord("#"):
            comments.append(line)
            header_end += len(line) + 1
        elif len(line.split()) == 2:
            words = line.split()
            width = int(words[0])
            height = int(words[1])
            header_end += len(line) + 1
        else:
            max_c = int(line)
            header_end += len(line) + 1
            break

    return header_end, width, height, max_c, comments


def createHeader(width, height, max_c, comments=""):
    return "P6\n"+comments+"\n"+str(width)+" "+str(height)+"\n"+str(max_c)+"\n"
