import utils
import findCard
import process

from bson.objectid import ObjectId
from pymongo import MongoClient
import cv2

client = MongoClient()
db = client.businessCards
BusinessCards = db.businessCards

FOLDER_PATH = '/home/aaron/Documents/RPI/semester_4/computational_vision/project/BusinessCardReader/server/uploads/'

def handlePicture(cardPath):
    # card = BusinessCards.find_one({'_id': Objectid(cardId)})
    # path = '../' + card['filename']
    img = utils.readImage(cardPath)
    good, card = findCard.findCard(img)
    regions, text = process.processCard(card)
    processedCard = process.drawRegions(card, regions)
    cards = [('Original', img), (str(text), processedCard)]
    print text
    utils.display(cards)

def processCard(cardId):
    card = BusinessCards.find_one({'_id': ObjectId(cardId)})
    cardPath = FOLDER_PATH + card['filename']
    img = utils.readImage(cardPath)
    good, cardImg = findCard.findCard(img)
    regions, text = process.processCard(cardImg)
    processedCard = process.drawRegions(cardImg, regions)
    print card['filename']
    cv2.imwrite('./static/processed/' + card['filename'], processedCard)
    card['processed'] = True
    card['text'] = text
    card['regions'] = regions
    card['good'] = good
    BusinessCards.save(card)

if __name__ == "__main__":
    handlePicture('')
