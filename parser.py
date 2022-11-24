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

def blockLength(data, blockstart):
    return bToInt(data[blockstart:blockstart+4])

def headerParser(image, data, blockstart):
    image['Largeur'] = bToInt(data[blockstart:blockstart+4])
    image['Hauteur'] = bToInt(data[blockstart+4:blockstart+8])

def commentParser(image, data, blockstart, length):
    image['Commentaires'] += bToStr(data[blockstart:blockstart+length])

def dataParser(imType, data, blockstart, length):
    usefulData = []
    if imType == 0:
        for bit in BitArray(data[blockstart:blockstart+length]).bin:
            usefulData.append(bit)
    elif imType == 1 or imType == 2:
        for i in range(blockstart, blockstart+length):
            usefulData.append(bToInt(data[i:i+1]))
    elif imType == 3:
        for i in range(blockstart, blockstart+length, 3):
            usefulData.append([bToInt(data[i:i+1]), bToInt(data[i+1:i+2]), bToInt(data[i+2:i+3])])
    return usefulData

def paletteParser(image, data, blockstart, length):
    colors = []
    for i in range(blockstart, blockstart+length, 3):
        colors.append([bToInt(data[i:i+1]), bToInt(data[i+1:i+2]), bToInt(data[i+2:i+3])])
    image['Palette'] = colors

def checkImageWeight(imType, lengthD, height, width):
    if imType==0:
        expectedDataLength = math.ceil(height*width/8)
    elif imType==1 or imType==2:
        expectedDataLength = height*width
    elif imType==3:
        expectedDataLength = height*width*3
    else:
        raise Exception("Unknown type of pixel...")
    return lengthD == expectedDataLength

def findImType(data):
    cursor = 8
    while data[cursor:cursor+1] != b'H':
        cursor+=1
    cursor+=4+4+4+1
    return bToInt(data[cursor:cursor+1])

def imageType(n):
    if not n:
        return '0 (noir et blanc)'
    elif n==1:
        return '1 (niveaux de gris)'
    elif n==2:
        return '2 (palette)'
    elif n==3:
        return '3 (couleurs)'

def parser(file):
    data = load_file(file)

    if bToStr(data[:8]) != 'Mini-PNG':
        raise Exception('What is the magic number??')

    imType = findImType(data)
    usefulD = []
    cursor = 8
    image = dict()
    image['Largeur']=0
    image['Hauteur']=0
    image['Type de pixel'] = imageType(imType)
    image['Commentaires'] = ''
    image['Palette'] = 'Pas de palette pour cette image !'
    lengthD=0
    hasH = False
    hasD = False
    hasC = False

    blocktype = blockType(data, cursor)

    while blocktype:
        if blocktype=='H':
            cursor+=5
            headerParser(image, data, cursor)
            cursor+=4+4+1
            hasH = True
        elif blocktype=='C':
            cursor+=1
            length=blockLength(data, cursor)
            cursor+=4
            commentParser(image, data, cursor, length)
            cursor+=length
            hasC = True
        elif blocktype=='D':
            cursor+=1
            length=blockLength(data, cursor)
            cursor+=4
            usefulD += dataParser(imType, data, cursor, length)
            lengthD+=length
            cursor+=length
            hasD = True
        elif blocktype=='P':
            cursor+=1
            length=blockLength(data, cursor)
            cursor+=4
            paletteParser(image, data, cursor, length)
            cursor+=length
        else:
            raise Exception("Unknown block type")

        blocktype = blockType(data, cursor)

    if not hasH:
        raise Exception("Where is your header??")
    elif not hasD:
        raise Exception("Where is your data??")
    elif not hasC:
        image['Commentaires']+= 'No comment...'
    elif not checkImageWeight(imType, lengthD, image['Hauteur'], image['Largeur']):
        raise Exception("Issue with data length...")

    return imType, image, usefulD

## Affichage image
def print_minipng(imType, data, palette, height, width):
    for i in range(height):
        for value in data[i*width:(i+1)*width]:
            if imType==0:
                if not int(value):
                    print('x', end='')
                else:
                    print(' ', end='')
            elif imType==1:
                print(value, end=' ')
            elif imType==2:
                print(palette[value], end=' ')
            elif imType==3:
                print(value, end=' ')
        print()


## Programme principal
if __name__ == "__main__":
    try:
        imType, image, data = parser(sys.argv[1])
        for key, value in image.items():
            print(key, " : ", value)
        print_minipng(imType, data, image['Palette'], image['Hauteur'], image['Largeur'])
    except Exception as e:
        print(e)