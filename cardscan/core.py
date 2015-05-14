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
    goodTransform, cardImg = findCard.findCard(img)
    goodBlur = process.checkBlur(cardImg)
    regions, text = process.processCard(cardImg)
    processedCard = process.drawRegions(cardImg, regions)
    suggestedFields = process.guessFields(regions, text)
    imgWrite = processedCard[::, ::, ::-1]
    cv2.imwrite('server/static/processed/' + card['filename'], imgWrite)
    card['processed'] = True
    card['text'] = text
    card['regions'] = regions
    card['suggested'] = suggestedFields

    if not goodTransform:
        card['warnings'] = ['Detected a bad transformation']
    if not goodBlur:
        warningMsg = 'Detected a blurry image'
        if 'warnings' in card:
           card['warnings'].append(warningMsg)
        else:
            card['warnings'] = [warningMsg]

    BusinessCards.save(card)

if __name__ == "__main__":
    handlePicture('')
