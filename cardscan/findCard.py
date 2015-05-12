#Tested images that work Droid 7,12, 14,17,19,21,22, 23,24, 25, maybe 26,30
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math as m
import process
import os


def ptDist(pt1, pt2):
    return m.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2 )

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

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
    #image = cv2.bilateralFilter(image, 5, 500, 120)
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #Processing image to improve reliability of finding corners

    sigma = 1
    ksize = (4*sigma+1,4*sigma+1)
    imgray = cv2.GaussianBlur(imgray, ksize, sigma)

    kernel = np.ones((5,5),np.uint8)

    imgray = cv2.morphologyEx(imgray,cv2.MORPH_OPEN,kernel)
    imgray = cv2.morphologyEx(imgray,cv2.MORPH_CLOSE,kernel)
    imgray = cv2.Canny(imgray,40,75)
    return imgray
#Takes edited picture and find corners. Returns transformation of original image croped and transformed

def findAndTransform(processed, original, scale):
    image = cv2.resize(original, (original.shape[1]/scale, original.shape[0]/scale))
    #Finding the corners
    dst = cv2.cornerHarris(processed,4,3,.03)

    #Finding Harris lines
    lines = cv2.HoughLines(processed,1,2*np.pi/180,35)
    my_lines = []
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        #making list of all Hough lines found
        my_lines.append( line( np.array( [x0,y0] ), np.array( [x1,y1] ) ) )
        cv2.line(image,(x1,y1),(x2,y2),(0,0,255),1)
    line_corners = []
    x_corner = []
    y_corner = []
    #F
    for i in range(len(my_lines)):
        for j in range(len(my_lines)):
            pt = intersection(my_lines[i], my_lines[j])

            if pt == False:
                continue
            elif pt[1] > image.shape[0] or pt[0] > image.shape[1] or pt[0] < 0 or pt[1] < 0:
                continue
            else:
                #Changing pt to numpy coordinate from opencv for sanity
                pt = pt[::-1]
                x_corner.append(pt[0])
                y_corner.append(pt[1])
                line_corners.append(pt)
                #image[int(pt[0]), int(pt[1])] = [255,0,255]
    x_corner = np.array(x_corner)
    y_corner = np.array(y_corner)
    #image[dst>0.15*dst.max()]=[255,0,255]
    """ Ploting images for testing
    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    plt.imshow(processed)
    plt.gray()
    plt.show()
    """
    #Finds locations of on image where corners could be
    mask =  dst>0.02*dst.max()
    locs = np.column_stack(np.where(mask))

    """
    Checks for good points by comparing Hough line intersections
    to Harris corners and comparing the distance from each and if found a close
    point is found then point is approved to check as a corner
    """
    good_points = []
    mask = []
    for pt in locs:
        x = pt[0]

        y = pt[1]
        x_diff = x_corner-x
        y_diff = y_corner-y
        diff = (x_diff**2 + y_diff**2)**.5
        #Experimental good distance
        #Number can be hard coded for now since all images are scaled to around same size
        tmpMask = diff < 5

        if np.sum(tmpMask) > 0:
            mask.append(True)
        else:
            mask.append(False)

    for i in range(len(locs)):
        if mask[i]:
            good_points.append(locs[i])

    uLeft = np.array(processed.shape[:2])
    lLeft = [0, processed.shape[1] ]
    uRight = [processed.shape[0], 0]
    lRight = [0,0]
    #Loops though possible corners and decided if it is one of the four on the rectangle
    for pair in good_points:
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

def findCard(img):
    """
    Method to combine funtionality, takes an image and optionally a scale
    Returns a boolean and cropped and transformed image
    """
    approved = 50000
    scale = int(m.sqrt(img.shape[0]*img.shape[1]/approved))
    edits = processCard(img,scale)
    good, cropped = findAndTransform(edits, img, scale)
    return good, cropped

def main():
    imgs = os.listdir("Droid")


    for img in imgs:
        image_o = cv2.imread("Droid/"+img)
        good, dst = findCard(image_o)
        if good:

            plt.imshow(dst)
            plt.axis("off")
            plt.show()

            #process.processCard(dst)

if __name__ == '__main__':
    main()
