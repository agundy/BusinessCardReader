import numpy as np
import cv2
from matplotlib import pyplot as plt
import subprocess

import utils
import findCard

DEBUG = False
PHONEALIASES = ['ph.', 'phone', 'tel.']

def parseText(text):
    text = text.strip()
    # Replace long lines with regular lines
    text = text.replace('\xe2\x80\x94', '-')
    # Remove left single quotation mark
    text = text.replace('\xe2\x80\x98','')
    text = text.replace('\xef','i')
    text = text.replace('\xc3\xa9', '6')
    text = text.decode('utf-8', 'ignore')
    return text

def checkBlur(img):
    img = cv2.resize(img, (1000,600))
    grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grayImg = cv2.equalizeHist(np.copy(grayImg))
    fft = np.fft.fft(grayImg)
    avgFFT = np.average(fft)
    threshFFT_x, threshFFT_y = np.where(fft> 1.25*avgFFT)
    return len(threshFFT_x) > 130000

def getText(img, regions, debug=False):
    textChunks = []
    imgChunks = []
    for region in regions:
        x1, y1, x2, y2 = region
        # Clip region and extract text
        chunk = img[y1:y2, x1:x2, ::]
        ret,chunk = cv2.threshold(chunk,140,255,0)
        cv2.imwrite('tmp.jpg', chunk)
        subprocess.call(['tesseract', 'tmp.jpg', 'tmp'])
        f = open('tmp.txt')
        lines = []
        for line in f:
            print line.strip()
            if line.strip() != '':
                lines.append(parseText(line))
        textChunks.append(lines)
        imgChunks.append(chunk)
        f.close()
        subprocess.call(['rm', 'tmp.jpg', 'tmp.txt'])
    if DEBUG:
        display = [(str(text), imgChunks[i]) for i, text in enumerate(textChunks)]
        utils.display(display[:10])
        utils.display(display[10:20])
    return textChunks

def getRegions(img):
    grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(grayImg,100,200,apertureSize = 3) 
    if DEBUG:
        utils.display([('Contours', edges)])
    kernel = np.ones((3,3),np.uint8)
    edges = cv2.dilate(edges,kernel,iterations = 14)
    edges = 255-edges
    # utils.display([('', edges)])
    contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if DEBUG:
        utils.display([('Contours', edges)])
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
    return regions

def drawRegions(img, regions):
    for x1, y1, x2, y2 in regions:
        cv2.rectangle(img, (x1,y1), (x2,y2), (0, 255, 0), 2)

    if DEBUG:
        utils.display([('Regions', img)])
    return img

def processCard(img):
    regions = getRegions(img)
    text = getText(img, regions)
    return regions, text

def guessFields(regions, textFields):
    '''
    Function to guess which fields are which based of of properties of the text
    '''
    def checkForPhone(line):
        # Checks if any substrings of phone or related words are in the line
        for word in PHONEALIASES:
            if word in line:
                return True 
        return False
    def checkEmail(line):
        if '@' in line  and '.' in line:
            return True
        elif 'email' in line or 'e-mail' in line:
            return True
        else:
            return False
    def checkFax(line):
        if 'fax' in line:
            return True
        else:
            return False
    def checkWebsite(line):
        if 'www' in line:
            return True
        else:
            return False

    sizes = [(x2-x1)*(y2-y1) for x1,y1,x2,y2 in regions]
    sortedSizes = sorted(sizes)
    sortedSizes.reverse()

    suggestedFields = []

    for i in range(len(regions)):
        suggestedLinesField = []

        lines = textFields[i]
        size = sizes[i]
        lineCount = 0

        for line in lines:
            line = line.lower()
            if size == sortedSizes[0] and lineCount == 0:
                # Largest size suggest for company name
                suggestedLinesField.append('Company')
            elif checkForPhone(line):
                suggestedLinesField.append('Phone')
            elif checkFax(line):
                suggestedLinesField.append('Fax')
            elif checkWebsite(line):
                suggestedLinesField.append('Website')
            else:
                suggestedLinesField.append('')
            lineCount += 1
        lineCount = 0
        suggestedFields.append(suggestedLinesField)
    return suggestedFields

if __name__ == "__main__":
    # imgs = utils.getImages('../../stanford_business_cards/photos/', 5)
    imgs = utils.getImages('../our_cards/', 7)
    DEBUG = True
    # img = utils.readImage('../../stanford_business_cards/photos/004.jpg')
    # imgs = [('',img)]
    # utils.display(imgs)
    good, cardImg = findCard.findCard(imgs[6][1])
    regions, text = processCard(cardImg)
    processedCard = drawRegions(cardImg, regions)
    suggestedFields = guessFields(regions, text)
    utils.display([('card',processedCard)])

    # scores = []
    # for imgName, img in imgs:
    #     # regions, text = processCard(img)
    #     # guessFields(regions, text)
    #     try:
    #         good, cardImg = findCard.findCard(img)
    #     except:
    #         good = False
    #         pass
    #     if good:
    #         scores.append((checkBlur(cardImg), imgName, cardImg))

    # scores.sort()
    # for score in scores:
    #     print score[0], score[1]
    # imgs = [(str(score), img) for score, imgName, img in scores]
    # for i in range(len(imgs)/10+1):
    #     utils.display(imgs[i*10:i*10+10])
