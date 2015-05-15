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
    imgs = utils.g

def processCard(cardId):
    card = BusinessCards.find_one({'_id': ObjectId(cardId)})
    cardPath = FOLDER_PATH + card['filename']
    img = utils.readImage(cardPath)
    goodTransform, cardImg = findCard.findCard(img)
    goodBlur = process.checkBlur(cardImg)
    regions, text = process.processCard(cardImg)
    processedCard = process.drawRegions(cardImg, regions)
    suggestedFields = process.guessFields(regions, text)
    imgWrite = processedCard[::, ::, ::]
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
