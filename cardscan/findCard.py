import cv2
import numpy as np
from matplotlib import pyplot as plt
import math as m
import process
import os
import random as r

"""
Sorting methods for determining most likely corners
"""
def uLeftSort(pt):
    return pt[0] + pt[1]

def lLeftSort(pt):
    return -1*(pt[0] - pt[1])

def uRightSort(pt):
    return -1*(pt[1] - pt[0])

def lRightSort(pt):
    return -1*(pt[0] + pt[1])

#End of Sort Functions

#Finds distance between two points
def distance(pt1,pt2):
    return m.sqrt( (pt1[0]-pt2[0])**2 +  (pt1[1]-pt2[1])**2 )

"""
Function to remove large clusters
Goal of function was in the future can guess better corners
by knowing where specific guesses are rather than having to check through
so many points that are right next to eachother
"""
def sparcify(pts):
    sparce = []
    while(len(pts) > 0):
        point = pts[int(r.random() * len(pts))]
        sparce.append(point)
        pts.remove(point)
        toRemove = []
        for pt in pts:
            if distance(pt,point) < 3:
                toRemove.append(pt)
        for pt in toRemove:
            pts.remove(pt)
    return sparce

"""
Function to find a line in Ax + By + C = 0 form
Also approves the slope of the line so only vertical and horizontal lines are
made. This limits how distorted the card can be in an image but improves
results in flatter cases. By making the angle range smaller more distored
cards can be found
"""
def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    angle = 90
    #If B is 90 then there is a 90 degree angle and causes a divide by zero
    if not B == 0:
        slope  = -1*A/float(B)
        angle = m.atan(slope) * 180 / np.pi
        angle = m.fabs(angle)
    #Can limit range to improve straighter examples, fails when card is less stright
    if angle < 70 and angle > 5:
        return False
    else:
        return A, B, -C

def intersection(L1, L2):
    #Check to make sure lines have some difference between them in angle

    #Massive slope in case line is vertical
    slope1 = 99999999999999
    if not L1[1] == 0:
        slope1 = -1*L1[0]/float(L1[1])
    slope2 = 99999999999999
    if not L2[1] == 0:
        slope2 = -1*L2[0]/float(L2[1])
    if slope1 < slope2:
        tmp = slope1
        slope1 = slope2
        slope2 = tmp
    angle = m.atan( (slope1-slope2) / (1+slope1*slope2) ) * 180 / np.pi
    """
    If two lines do not differ by a large enough angle then the intersection
    should be ignored since the goal is to look for corners not necessarily
    just intersections
    """
    if m.fabs(angle) < 35:
        return False
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
    try:
        p12 = m.sqrt( (pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2 )
        p13 = m.sqrt( (pt1[0] - pt3[0])**2 + (pt1[1] - pt3[1])**2 )
        p23 = m.sqrt( (pt2[0] - pt3[0])**2 + (pt2[1] - pt3[1])**2 )
        #From law of Cosines
        angle = m.acos( (p12**2+p13**2-p23**2) / (2.0*p12*p13) )
        return angle
    except(ZeroDivisionError):
        return 0

#Checks to see if the four corners form approximately right angles
def angleApproval(points):
    total_angle = m.pi * 2

    for i in range(len(points) - 1):
        angle = find_angle(points[i], points[i-1], points[i+1])
        if not checkAngle(angle):
            return False
        total_angle -= angle
    if not checkAngle(total_angle):
        return False
    else:
        return True

"""
Function to turn image into canny edges to find corners of a card
Gaussian blur was previously used and successful, but recently the
bilateral filter seems to give better results
"""
def processCard(image_o,scale):
    #Scale image down so functions work better and turns to greyscale
    image = cv2.resize(image_o, (image_o.shape[1]/scale, image_o.shape[0]/scale))
    image = cv2.bilateralFilter(image, 5, 100, 25)
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #Processing image to improve reliability of finding corners
    """
    sigma = 1
    ksize = (4*sigma+1,4*sigma+1)
    imgray = cv2.GaussianBlur(imgray, ksize, sigma)
    """
    kernel = np.ones((5,5),np.uint8)

    imgray = cv2.morphologyEx(imgray,cv2.MORPH_OPEN,kernel)
    imgray = cv2.morphologyEx(imgray,cv2.MORPH_CLOSE,kernel)

    imgray = cv2.Canny(imgray,40,55)

    return imgray

#Takes edited picture and find corners. Returns transformation of original image croped and transformed
def findAndTransform(processed, original, scale):
    image = cv2.resize(original, (original.shape[1]/scale, original.shape[0]/scale))
    #Finding the corners
    dst = cv2.cornerHarris(processed,4,3,.03)

    #Finding Harris lines
    lines = cv2.HoughLines(processed,1,2*np.pi/180,33)
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
        foundLine = line( np.array( [x0,y0] ), np.array( [x1,y1] ) )
        if foundLine == False:
            continue
        else:
            my_lines.append( foundLine )
            cv2.line(image,(x1,y1),(x2,y2),(0,0,255),1)
    line_corners = []
    x_corner = []
    y_corner = []
    #Finding intersection of lines
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
    x_corner = np.array(x_corner)
    y_corner = np.array(y_corner)
    #image[dst>0.15*dst.max()]=[255,0,255]
    """ Image ploting for debugging and testing
    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    plt.imshow(processed)
    plt.gray()
    plt.show()
    """
    #Finds locations of on image where corners could be
    mask =  dst>0.04*dst.max()
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
        tmpMask = diff < 10

        if np.sum(tmpMask) > 0:
            mask.append(True)
        else:
            mask.append(False)

    for i in range(len(locs)):
        if mask[i]:
            good_points.append(tuple(locs[i]))

    #Gets rid of points that are too close to eachother
    """ Commented since un-used, but function works
    good_points = sparcify(good_points)

    for pt in good_points:
        image[pt[0], pt[1]] = [255,10,255]

    plt.imshow(image)
    plt.show()
    """

    #Sorting of points by top left/right
    uLeftOrder = sorted(good_points, key=uLeftSort)
    uRightOrder = sorted(good_points, key=uRightSort)
    lLeftOrder = sorted(good_points, key=lLeftSort)
    lRightOrder = sorted(good_points, key=lRightSort)
    orders = [uLeftOrder, uRightOrder, lLeftOrder, lRightOrder]

    uLeft = uLeftOrder[0]
    uRight = uRightOrder[0]
    lLeft = lLeftOrder[0]
    lRight = lRightOrder[0]
    points = [uLeft,uRight,lRight,lLeft]

    angle_check = angleApproval(points)

    #Returns the points back to normal size of the image
    uLeft = np.array(uLeft) * scale
    uRight = np.array(uRight) * scale
    lLeft = np.array(lLeft) * scale
    lRight = np.array(lRight) * scale
    points = [uLeft,uRight,lRight,lLeft]

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
    approved = 52500
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
