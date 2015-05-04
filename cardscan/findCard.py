#Tested images that work Droid 7,12, 14,17,19,21,22, 23,24, 25, maybe 26,30
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math as m
import process


#Angle check, if angle is greater than 33% off from what it should be (pi/2)
def checkAngle(angle):
    return m.pi/2 - m.pi/2*.33 < angle and angle < m.pi/2 + m.pi/2*.33

def find_angle(pt1,pt2,pt3):
    #pt1 is the vertex of the three points forming the angle
    p12 = m.sqrt( (pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2 )
    p13 = m.sqrt( (pt1[0] - pt3[0])**2 + (pt1[1] - pt3[1])**2 )
    p23 = m.sqrt( (pt2[0] - pt3[0])**2 + (pt2[1] - pt3[1])**2 )
    #From law of Cosines
    angle = m.acos( (p12**2+p13**2-p23**2) / (2.0*p12*p13) )
    return angle

def processCard(image_o,scale):
    #Scale image down so functions work better and turns to greyscale
    image = cv2.resize(image_o, (image_o.shape[1]/scale, image_o.shape[0]/scale))
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #Processing image to improve reliability of finding corners

    sigma = 2
    ksize = (4*sigma+1,4*sigma+1)
    imgray = cv2.GaussianBlur(imgray, ksize, sigma)

    kernel = np.ones((5,5),np.uint8)

    imgray = cv2.morphologyEx(imgray,cv2.MORPH_OPEN,kernel)
    imgray = cv2.morphologyEx(imgray,cv2.MORPH_CLOSE,kernel)

    return imgray
#Takes edited picture and find corners. Returns transformation of original image croped and transformed
def findAndTransform(processed, original, scale):
    #Finding the corners
    dst = cv2.cornerHarris(processed,4,3,.03)
    dst = cv2.dilate(dst,None)
    image = cv2.resize(original, (original.shape[1]/scale, original.shape[0]/scale))

    #Finds locations of on image where corners could be
    mask =  dst>0.02*dst.max()
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
    points = [uLeft,uRight,lRight,lLeft]
    total_angle = m.pi * 2
    angle_check = True
    for i in range(len(points) - 1):
        angle = find_angle(points[i], points[i-1], points[i+1])
        if not checkAngle(angle):
            angle_check = False
        total_angle -= angle
    if not checkAngle(total_angle):
        angle_check = False
    length = int(m.sqrt((uLeft[0]-uRight[0])**2 + (uLeft[1]-uRight[1])**2))
    width = int(m.sqrt((uLeft[0] - lLeft[0])**2 + (uLeft[1] - lLeft[1])**2 ))
    #Maps corners to new image size
    pts1 = np.float32([uLeft[::-1],uRight[::-1],lLeft[::-1],lRight[::-1]])
    pts2 = np.float32([[0,0],[length,0],[0,width],[length ,width]])

    #Transforms and returns scan like image
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(original, M,(length,width))
    return angle_check, dst

def findCard(img, scale = 10):
    """
    Method to combine funtionality, takes an image and optionally a scale
    Returns a boolean and cropped and transformed image
    """
    edits = processCard(img,scale)
    good, cropped = findAndTransform(edits, img, scale)
    return good, cropped

def main():

    path = "/media/andrew/E0D419A0D41979CC/Users/Andrew Batbouta/Dropbox/Droid/"
    for i in range(10,35):
        image_o = cv2.imread(path+'0'+str(i)+'.jpg')
    
        good, dst = findCard(image_o)#findAndTransform(edits, image_o, scale)
        if good:

            process.processCard(dst)

if __name__ == '__main__':
    main()
