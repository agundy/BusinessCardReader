import numpy as np
import cv2
from matplotlib import pyplot as plt
import subprocess

import utils

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
                lines.append(line.strip())
        textChunks.append(lines)
        utils.display([(str(lines), chunk)])
        f.close()
    return textChunks

def getRegions(img):
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,0,255,0)
    edges = cv2.Canny(imgray,150,200,apertureSize = 3) 
    # Find contours and close
    kernel = np.ones((3,3),np.uint8)
    edges = cv2.dilate(edges,kernel,iterations = 12)
    binaryImg = cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel)
    contours, hierarchy = cv2.findContours(binaryImg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # Only take contours of a certain size
    regions = []
    for contour in contours:
        imgW, imgH, _ = img.shape
        [x, y, w, h] = cv2.boundingRect(contour)
        if w < 50 or h < 50:
            pass
        elif w > .9*imgW or h > .9*imgH:
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

if __name__ == "__main__":
    im = cv2.imread('../../stanford_business_cards/scans/011_002.jpg')
    regions = getRegions(im)
    utils.display([('', drawRegions(im, regions))])
    text = getText(im, regions)
    print text
