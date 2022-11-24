#!/bin/python3

import sys

## Écriture d'un fichier Mini-PNG avec la lettre O
def black_and_white_minipng(pathfile, height, width, data, comment=''):
    f = open(pathfile, 'wb')
    datas = b'Mini-PNGH\x00\x00\x00\t'

    heightInBytes = height.to_bytes(4, 'big')
    widthInBytes = width.to_bytes(4, 'big')
    datas+=heightInBytes+widthInBytes+b'\x00'     #le \x00 correspond au type de pixel
    if comment:
        datas+=b'C'
        lengthCinBytes = len(comment).to_bytes(4, 'big')
        commentinBytes = comment.encode()
        datas+=lengthCinBytes+commentinBytes
    datas+=b'D'
    lengthDinBytes = len(data).to_bytes(4, 'big')
    datas+=lengthDinBytes+data

    f.write(datas)
    f.close()

## Programme principal
minipng_path = './O.mp'
width = 8
height = 8
datas = b'\xc3\xbd~~~~\xbd\xc3'
comments = 'La lettre O'

if __name__ == "__main__":
    black_and_white_minipng(minipng_path, width, height, datas, comment=comments)