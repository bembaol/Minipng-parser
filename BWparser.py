#!/bin/python3

from bitstring import BitArray
import math
import sys

##Parser d'images Mini-png noir et blanc

def load_file(file):
    return open(file, 'rb').read()

def bToInt(data):
    return int.from_bytes(data, 'big')

def bToStr(data):
    return data.decode('UTF-8')

def blockType(data, blockStart):
    blockType = bToStr(data[blockStart:blockStart+1])
    return blockType

def blockCorDLength(data, blockstart):
    return bToInt(data[blockstart:blockstart+4])

def headerParser(image, data, blockstart):
    image['Largeur'] = bToInt(data[blockstart:blockstart+4])
    image['Hauteur'] = bToInt(data[blockstart+4:blockstart+8])
    image['Type de pixel'] = imageType(bToInt(data[blockstart+8:blockstart+9]))

def commentParser(image, data, blockstart, length):
    image['Commentaires'] += "\n"+bToStr(data[blockstart:blockstart+length])

def dataParser(data, blockstart, length):
    usefulData = BitArray(data[blockstart:blockstart+length]).bin
    return usefulData


def imageType(n):
    if not n:
        return '0 (noir et blanc)'
    elif n==1:
        return '1 (niveaux de gris)'
    elif n==2:
        return '2 (palette)'
    elif n==3:
        return '3 (couleurs)'

def BWparser(file):
    data = load_file(file)

    if bToStr(data[:8]) != 'Mini-PNG':
        raise Exception('What is the magic number??')

    cursor = 8
    image = dict()
    image['Largeur']=0
    image['Hauteur']=0
    image['Type de pixel'] = ''
    image['Commentaires'] = ''
    lengthD=0
    usefulData = ''
    hasH = False
    hasD = False

    blocktype = blockType(data, cursor)

    while blocktype:
        if blocktype=='H':
            cursor+=5
            headerParser(image, data, cursor)
            cursor+=4+4+1
            hasH = True
        elif blocktype=='C':
            cursor+=1
            length=blockCorDLength(data, cursor)
            cursor+=4
            commentParser(image, data, cursor, length)
            cursor+=length
        elif blocktype=='D':
            cursor+=1
            length=blockCorDLength(data, cursor)
            cursor+=4
            usefulData += dataParser(data, cursor, length)
            lengthD+=length
            cursor+=length
            hasD = True
        else:
            raise Exception("Unknown block type")

        blocktype = blockType(data, cursor)

    if not hasH:
        raise Exception("Where is your header??")
    elif not hasD:
        raise Exception("Where is your data??")

    expectedDataLength = math.ceil(image['Largeur']*image['Hauteur']/8)

    if lengthD != expectedDataLength:
        raise Exception("Issue with data length...")

    return image, usefulData

## Affichage images noir et blanc
def print_bw_minipng(data, width, height):
    for i in range(height):
        for bit in data[i*width:(i+1)*width]:
            if not int(bit):
                print('x', end='')
            else:
                print(' ', end='')
        print()


## Programme principal
if __name__ == "__main__":
    try:
        image, data = parser(sys.argv[1])
        for key, value in image.items():
            print(key, " : ", value)
        print_bw_minipng(data, image['Largeur'], image['Hauteur'])
    except Exception as e:
        print(e)

