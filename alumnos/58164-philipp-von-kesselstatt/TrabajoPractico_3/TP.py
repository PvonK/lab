#!/usr/bin/python3

import os
import array
import argparse
import concurrent.futures as fut
import matplotlib.pyplot as plot


class InvalidFormat(Exception):
    def __init__(self, message):
        print(message)


class NoFile(Exception):
    def __init__(self, message):
        print(message)


# El objeto ImagenPPM tiene:
# -path (el path directorio del archivo)
# -size (el tamaño de la imagen)
# -image (el string leido del archivo)
# -header (el header de la imagen PPM)
# -body (el cuerpo de la imagen PPM)
# -imageList (lista con los pixels de la imagen como valores RGB)
# --------------------------------------------------------------------------
# El objetoColorChannel tiene:
# -header (el header de la imagen PPM)
# -filterImage (lista con los valores RGB de la imagen con un solo color)
# -customFilterImage (lista como filterImage pero con la intensidad cambiada)
# +intensity(intensity) (cambia el valor del filtro con un porcentaje)
# +write(path, name) (escribe la imagen en un archivo)
class ImagePPM():
    def __init__(self, path, name, bloq=0):

        # error si no se ingresa una imagen
        if not name:
            raise NoFile("No file entered")

        # error si el tamaño de bloque es negativo
        if bloq < 0:
            raise ValueError(
                    "Negative values for the read block size are invalid"
                    )

        # error si la imagen no es .ppm
        if not name.endswith(".ppm"):
            raise InvalidFormat("image is an invalid format")

        self.path = path

        # leo la imagen
        self.size = os.path.getsize(path + name)
        with open(self.path + name, "rb") as archivo:
            if bloq == 0:
                self.image = archivo.read()
            else:
                self.image = b""
                for num in range(round(self.size/bloq + 0.5)):
                    self.image += archivo.read(bloq)

        # busco el header de la imagen
        cont = 0
        whitespace = 0
        for num in range(len(self.image)):
            item = self.image[num]

            if chr(item) == "\n":
                whitespace += 1
            elif chr(item) == "#":
                whitespace -= 1

            if whitespace == 3:
                cont += 1
            if cont == 2:
                self.header = self.image[:num]
                break

        # separo el header de el resto de la imagen
        self.body = self.image.replace(self.header, b"")
        self.header = self.header.decode()

        # creo una lista con los pixeles como ints
        self.imageList = [i for i in self.body]


class ColorChannel():
    def __init__(self, color, imageList, header, intensity=1):

        # print(os.getpid())

        # error si la intensidad es negativa
        if intensity < 0:
            raise ValueError("Negative values for color intensity are invalid")

        # asigno el header y el valor maximo de color de los pixels
        self.header = header
        self.max_c = int(self.header.split()[-1])

        # inicializo la lista de valores de los colores como una lista de 0
        self.filterImage = [0 for i in imageList]

        # asigno el valor de la imagen solamente
        # en las posiciones del color indicado
        for i in range(color, len(imageList), 3):
            self.filterImage[i] = imageList[i]

        # creo la imagen de intensidad cambiada
        self.customFilterImage = [int(i * intensity)
                                  if i * intensity <= self.max_c
                                  else self.max_c
                                  for i in self.filterImage]

    # metodo para volver a cambiar la intensidad si es necesario
    def intensity(self, intensity):
        self.customFilterImage = [int(i * intensity)
                                  if i * intensity <= self.max_c
                                  else self.max_c
                                  for i in self.filterImage]

        return self.customFilterImage

    # metodo que escribe la imagen en un archivo
    def write(self, path, name):
        image = array.array('B', self.customFilterImage)

        with open(path + name, "wb", os.O_CREAT) as x:
            x.write(bytearray(self.header, 'ascii'))
            image.tofile(x)


# metodo para juntar imagenes a un solo archivo
def joinImages(path, name, header, *args):
    # determino el valor de color maximo
    max_c = int(header.split()[-1])

    # verifico que todas las imagenes son del mismo tamaño
    for item in args:
        if len(item) != len(args[0]):
            raise Exception

    # sumo los colores de todas las imagenes para cada pixel
    # si la suma es mayor al valor maximo de color se le asigna el valor maximo
    combination = [sum(i) if sum(i) <= max_c else max_c for i in zip(*args)]

    # escribo la nueva imagen en un archivo
    image = array.array('B', combination)

    with open(path + name, "wb", os.O_CREAT) as x:
        x.write(bytearray(header, 'ascii'))
        image.tofile(x)


# metodo para los procesos hijos
def child_process(path, name, color, imageList, header, intensity):

    # creo un canal de color
    channel = ColorChannel(color, imageList, header, intensity)

    # escribo el canal en un archivo
    channel.write(path, name)

    return channel.customFilterImage


def histograma(r, g, b):
    threeColors = []
    for color, num in zip([r, g, b], range(3)):
        lista = []
        for i in range(num, len(color), 3):
            lista.append(color[i])
        threeColors.append(lista)
    plot.hist(threeColors, color=["red", "green", "blue"])
    plot.show()


# main del programa
def main():

    # argumentos
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--fileppm", help="ppm file you want to open")
    parser.add_argument("-n", "--bloque", type=int, default=0,
                        help="byte block size")
    parser.add_argument("-r", "--red", type=float, default=1,
                        help="intensity of the red channel")
    parser.add_argument("-g", "--green", type=float, default=1,
                        help="intensity of the green channel")
    parser.add_argument("-b", "--blue", type=float, default=1,
                        help="intensity of the blue channel")

    args = parser.parse_args()

    path = __file__.replace("TP.py", "")
    name = args.fileppm

    # instancio la clase image con la imagen que se ingreso por argumento
    i = ImagePPM(path, name, args.bloque)

    # creo los procesos hijos para que separen los tres canales de color
    with fut.ProcessPoolExecutor() as colores:

        r = colores.submit(child_process, path, "red_output.ppm",
                           0, i.imageList, i.header, args.red
                           )

        g = colores.submit(child_process, path, "green_output.ppm",
                           1, i.imageList, i.header, args.green
                           )

        b = colores.submit(child_process, path, "blue_output.ppm",
                           2, i.imageList, i.header, args.blue
                           )

    # junto las imagenes
    joinImages(path, "final_output.ppm", i.header,
               r.result(), g.result(), b.result())

    histograma(r.result(), g.result(), b.result())

    # anuncio que termino de procesar la imagen
    print("termine")


if __name__ == "__main__":
    main()
