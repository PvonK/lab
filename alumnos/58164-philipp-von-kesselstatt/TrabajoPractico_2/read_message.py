import os
import argparse
import header_parser


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", type=str, default="out.ppm",
                        help="ppm file you want to open")
    parser.add_argument("-l", "--length", type=int, default=188,
                        help="interleave pixels")
    parser.add_argument("-s", "--size", type=int, default=1024,
                        help="size")

    args = parser.parse_args()

    # determino el path del script
    path = os.path.dirname(__file__) + "/"

    ppm = os.open(path + args.file, os.O_RDONLY)

    header_end = 0
    header = os.read(ppm, 100).splitlines()
    for item in header:
        header_end += len(item) + 1
        if item.startswith(b"#"):
            comment = item
        elif header.index(item) == 3:
            break

    comment = [int(i) for i in comment.split()[1:]]

    OFFSET, INTERLEAVE, L_TOTAL = comment

    os.lseek(ppm, header_end, 0)

    pixels = []
    for i in range(L_TOTAL*8):
        reading = os.read(ppm, 3)

        pixels.append(reading)
        os.lseek(ppm, INTERLEAVE*3-3, os.SEEK_CUR)

    c = 0
    byte = []
    for pixel in pixels:
        byte.append(pixel[c])
        c += 1
        if c == 3:
            c = 0

    code = "".join([str(i%2) for i in byte])

    code = [code[i-8:i] for i in range(8, len(code) + 1, 8)]

    x = []
    for s in code:
        s = [int(i) for i in s[::-1]]

        result = 0
        for i in range(len(s)):
            result += s[i]*(2**i)

        x.append(result)

    message = "".join(chr(i) for i in x)

    print(message)


if __name__ == "__main__":
    main()
