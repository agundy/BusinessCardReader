import numpy as np
import cv2
from matplotlib import pyplot as plt
import subprocess

import utils

def parseText(text):
    text = text.strip()
    # Replace long lines with regular lines
    text = text.replace('\xe2\x80\x94', '-')
    # Remove left single quotation mark
    text = text.replace('\xe2\x80\x98','')
    return text

def getText(img, regions):
    textChunks = []
    for region in regions:
        x1, y1, x2, y2 = region
        # Clip region and extract text
        chunk = img[y1:y2, x1:x2, ::]
        ret,chunk = cv2.threshold(chunk,150,255,0)
        cv2.imwrite('tmp.jpg', chunk)
        subprocess.call(['tesseract', 'tmp.jpg', 'tmp'])
        f = open('tmp.txt')
        lines = []
        for line in f:
            print line.strip()
            if line.strip() != '':
                lines.append(parseText(line))
        textChunks.append(lines)
        # utils.display([(str(lines), chunk)])
        f.close()
        subprocess.call(['rm', 'tmp.jpg', 'tmp.txt'])
    return textChunks

def getRegions(img):
    grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(grayImg,150,200,apertureSize = 3) 
    kernel = np.ones((3,3),np.uint8)
    edges = cv2.dilate(edges,kernel,iterations = 12)
    # binaryImg = cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel)
    contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # Only take contours of a certain size
    regions = []
    for contour in contours:
        imgH, imgW, _ = img.shape
        [x, y, w, h] = cv2.boundingRect(contour)
        if w < 50 or h < 50:
            pass
        elif w > .95*imgW or h > .95*imgH:
            pass
        else:
            regions.append((x, y, x+w, y+h))
    # cv2.drawContours(im, contours, -1, (0,255,0), 3)
    # utils.display([('', im)])
    return regions

def drawRegions(img, regions):
    for x1, y1, x2, y2 in regions:
        cv2.rectangle(img, (x1,y1), (x2,y2), (0, 255, 0))
    return img

def processCard(img):
    regions = getRegions(img)
    text = getText(img, regions)
    print text
    utils.display([('', drawRegions(img, regions))])

if __name__ == "__main__":
    imgs = utils.getImages('../../stanford_business_cards/scans/')
    for img in imgs:
        processCard(img[1])
    # im = utils.readImage('../../stanford_business_cards/scans/003_002.jpg')
    # print im
    # processCard(im)

