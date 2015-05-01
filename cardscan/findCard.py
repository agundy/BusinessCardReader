#Tested images that work Droid 12, 14,17,19,21,22, 23,24, 25, maybe 26,30
#TODO Error checking to make sure right angles are formed by corners
#TODO Add more methods to process cards if first on fails
#TODO Hard code less values and find ways to compute values
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math as m

def processCard(image_o,scale):
    #Scale image down so functions work better and turns to greyscale
    image = cv2.resize(image_o, (image_o.shape[1]/scale, image_o.shape[0]/scale))
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #Porcessing image to improve reliability of finding corners
    sigma = 2
    ksize = (4*sigma+1,4*sigma+1)
    imgray = cv2.GaussianBlur(imgray, ksize, sigma)
    test = imgray.flatten()
    summ = np.sum(test)
    attempt = int( summ / test.shape[0])
    ret,thresh = cv2.threshold(imgray,attempt,255,cv2.THRESH_BINARY_INV)

    kernel = np.ones((5,5),np.uint8)

    thresh = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel)
    thresh = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel)
    #Returns Canny edge version of srunk down original picture
    edges = cv2.Canny(thresh, 50,100)
    return edges
#Takes edited picture and find corners. Returns transformation of original image croped and transformed
def findAndTransform(processed, original, scale):
    #Finding the corners
    dst = cv2.cornerHarris(processed,4,3,.04)
    dst = cv2.dilate(dst,None)

    #Finds locations of on image where corners could be
    mask =  dst>0.10*dst.max()
    locs = np.column_stack(np.where(mask))
    uLeft = np.array(processed.shape[:2])
    lLeft = [0, processed.shape[1] ]
    uRight = [processed.shape[0], 0]
    lRight = [0,0]
    #Loops though possible corners and decided if it is one of the four on the rectangle
    for pair in locs:
        if uLeft[0] + uLeft[1] > pair[0] + pair[1]:
            uLeft = pair
        if lLeft[0] - lLeft[1] < pair[0] - pair[1]:
            lLeft = pair
        if uRight[1] - uRight[0] < pair[1] - pair[0]:
            uRight = pair
        if lRight[0] + lRight[1] < pair[0] + pair[1]:
            lRight = pair
    #Returns the points back to normal size of the image
    uLeft = np.array(uLeft) * scale
    uRight = np.array(uRight) * scale
    lLeft = np.array(lLeft) * scale
    lRight = np.array(lRight) * scale

    length = int(m.sqrt((uLeft[0]-uRight[0])**2 + (uLeft[1]-uRight[1])**2))
    width = int(m.sqrt((uLeft[0] - lLeft[0])**2 + (uLeft[1] - lLeft[1])**2 ))
    #Maps corners to new image size
    pts1 = np.float32([uLeft[::-1],uRight[::-1],lLeft[::-1],lRight[::-1]])
    pts2 = np.float32([[0,0],[length,0],[0,width],[length ,width]])

    #Transforms and returns scan like image
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(original, M,(length,width))
    return dst

def main():

    path = "/media/andrew/E0D419A0D41979CC/Users/Andrew Batbouta/Dropbox/Droid/"
    image_o = cv2.imread(path+'026.jpg')
    #Scale factor that seems to be working the best so far
    scale = 10
    edits = processCard(image_o, scale)
    dst = findAndTransform(edits, image_o, scale)
    plt.subplot(121)
    plt.imshow(dst)
    plt.axis("off")
    plt.subplot(122)
    plt.axis("off")
    plt.imshow(image_o)
    plt.show()


if __name__ == '__main__':
    main()
