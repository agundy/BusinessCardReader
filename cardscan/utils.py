import numpy as np
import cv2
from matplotlib import pyplot as plt
import glob
import random as rand

def readImage(imgName, grayscale=False):
    '''Simple function to read in an image and reverse the colors'''
    if grayscale:
        img = cv2.imread(imgName)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    else:
        img = cv2.imread(imgName)
        img = np.array(img[::,::,::-1])
    return img

def getImages(path, limit=20):
    '''
    INPUT: path: String of the folder 
        i.e. '../example_imgs'
    OUTPUT imgs: list of tuples with name and path 
        i.e. [('img1', '../example_imgs/img1')]
    '''
    path = './' + path + '/*'
    imageNames = glob.glob(path)
    imageNames = sorted(imageNames)
    imgs = []
    for i, imageName in enumerate(imageNames):
        if i >= limit and limit != -1:
            break
        imgPath = imageName.split('/')
        photoName = imgPath[len(imgPath)-1]
        img = readImage(imageName)
        print "Opening image %s" %imageName
        imgs.append((photoName, img))
    return imgs

def display(images):
    '''
    Takes a list of [(name, image, grayscaleImage, (keypoints, descriptor))]
    and displays them in a grid two wide
    '''
    # Calculate the height of the the plt. This is the hundreds digit
    size = int(np.ceil(len(images)/2.))*100
    # Number of images across is the tens digit
    size += 20
    count = 1
    plt.gray()
    for imgName, img in images:
        plt.subplot(size + count)
        plt.imshow(img)
        plt.title(imgName)
        count += 1
    plt.show()


if __name__ == "__main__":
    imgs = getImages('../../stanford_business_cards/scans', -1)
    display(imgs[:5])
