import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, url_for, abort
from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,
                                      UploadNotAllowed)
UPLOADED_PHOTOS_DEST = './uploads'
app = Flask(__name__, static_url_path='/static')
app.config.from_object(__name__)
app.config['UPLOADS_FOLDER'] = 'uploads/'

uploaded_photos = UploadSet('photos', IMAGES)
configure_uploads(app, uploaded_photos)

client = MongoClient()
db = client.businessCards
BusinessCards = db.businessCards

@app.route('/', methods=['GET'])
def index():
    cards = list(BusinessCards.find())
    return render_template('index.html', cards=cards)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = uploaded_photos.save(request.files['photo'])
        photo = {'filename': filename}
        print "Past"
        card_id = BusinessCards.insert(photo)
        print "Past"
        return redirect(url_for('show', card_id=card_id))
    return render_template('upload.html')

@app.route('/show/<card_id>')
def show(card_id):
    card = BusinessCards.find_one({'_id': ObjectId(card_id)})
    if card == None:
        abort(404)
    url = uploaded_photos.url(card['filename'])
    print url
    return render_template('show.html', card=card, url=url)

if __name__ == '__main__':
    app.run()
    
