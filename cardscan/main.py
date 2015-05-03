import numpy as np
import cv2
from matplotlib import pyplot as plt
import random as rand
import utils

def findText(img):
    grayImg = cv2.cvtColor(img[1], cv2.COLOR_BGR2GRAY)
    avg = np.average(grayImg)
    grayImg[::,::] -= avg
    ret, threshImg = cv2.threshold(grayImg, 70, 255, cv2.THRESH_BINARY)
    print threshImg
    image, contours, hierarchy = cv2.findContours(threshImg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.drawContours(img[1], contours, -1, (0,255,0), 3)
    # sobelImg = cv2.Sobel(grayImg, cv2.CV_64F,1,0,ksize=5)
    utils.display([(img[0], img), (img[0] + ' Gray', grayImg), (img[0] + ' Sobel', threshImg)])

if __name__ == "__main__":
    im = cv2.imread('../../stanford_business_cards/scans/001.jpg')
    imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(im, contours, -1, (0,255,0), 3)
    utils.display([('', im)])
    '''
    imgs = utils.getImages('../../stanford_business_cards/scans', 30)
    findText(imgs[4])
    utils.display(imgs[:5])
    '''
