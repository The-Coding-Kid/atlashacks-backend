import os

from flask import Flask, request, render_template, jsonify
from google.cloud import vision
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json
from tensorflow.keras.layers import Input, Lambda, Dense, Flatten, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications.vgg19 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
import numpy as np
import pandas as pd
import os
import cv2
import tensorflow as tf
from PIL import Image
import PIL

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})



app.config["IMAGE_UPLOADS"] = os.getcwd()



@app.route("/")
def home():
    return render_template("index.html")


# Route to upload image
@app.route('/upload-image', methods=['GET', 'POST'])
def upload_image():

    if request.method == "POST":
        if request.files:

            im = request.files["image"]
            
            
            # print(image + "Uploaded to Faces")
            # flash('Image successfully Uploaded to Faces.')
            im.save(os.path.join(app.config["IMAGE_UPLOADS"], im.filename))
            image = Image.open(os.path.join(app.config["IMAGE_UPLOADS"], im.filename))
            newsize = (200, 200)
            image = image.resize(newsize)
            im1 = image.rotate(-90, PIL.Image.NEAREST, expand = 1)
            im1.save(os.path.join(app.config["IMAGE_UPLOADS"], im.filename ))

            # Instantiates a client

            # The name of the image file to annotate
            file_name = os.path.abspath(im.filename)
            print(file_name)
            # Loads the image into memory
            with open(file_name, 'rb') as image_file:
                content = image_file.read()

            new_model = tf.keras.models.load_model('../model/ML_Models/mask_detector.h5')
            print(new_model)
            path = os.path.join(app.config["IMAGE_UPLOADS"], im.filename) 
            img = tf.keras.preprocessing.image.load_img(path, target_size=(200, 200))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0) # Create a batch

            predictions = new_model.predict(img_array)
            score = tf.nn.softmax(predictions[0])
            print(score)
            
            return jsonify()


@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == "POST":
        if request.files:
            dairy = False
            grains = False
            protein = False
            veggies = False
            fruits = False
            junk = False
            stars = 2

            contained = []
            notcontained = []

            grainfoods = ['Noodle', 'Pasta', 'Al dente', 'Sliced bread', 'Whole wheat bread', 'White bread', 'Bread', 'Bun', 'Hamburger', 'Stringozzi']
            proteinfoods = ['Hamburger', 'Meat', 'Patty', 'Seed', 'Nut', 'Cashew family', 'Ventricina']
            veggiefoods = ['Produce', 'Leaf vegetable', 'Vegetable', 'Root vegetable', 'Artichoke', 'Broccoli', 'Carrot', 'Carrots', 'Bean', 'Beans', 'Salad']
            fruitfoods = ['Fruit', 'Fruits', 'Apple', 'Apples', 'Orange', 'Produce', 'Salad']
            dairyfoods = ['Milk', 'milk', 'Lowfat milk', 'Yogurt', 'Butter', 'Ice cream', 'Cheese']
            junkfoods = ['French fries', 'Junk food', 'Fried food']

            im = request.files["image"]
            # print(image + "Uploaded to Faces")
            # flash('Image successfully Uploaded to Faces.')
            im.save(os.path.join(app.config["IMAGE_UPLOADS"], im.filename))

            # Instantiates a client
            client = vision.ImageAnnotatorClient()

            # The name of the image file to annotate
            file_name = os.path.abspath(im.filename)

            # Loads the image into memory
            with open(file_name, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # Performs label detection on the image file
            response = client.label_detection(image=image)
            labels = response.label_annotations

            # Performs object detection on the image file
            objects = client.object_localization(image=image).localized_object_annotations

            # Performs text detection on the image file
            response1 = client.text_detection(image=image)
            texts = response1.text_annotations

            for label in labels:
                if label.description in grainfoods:
                    grains = True
                if label.description in proteinfoods:
                    protein = True
                if label.description in veggiefoods:
                    veggies = True
                if label.description in dairyfoods:
                    dairy = True
                if label.description in fruitfoods:
                    fruits = True
                if label.description in junkfoods:
                    junk = True
            for text in texts:
                if text.description in grainfoods:
                    grains = True
                if text.description in proteinfoods:
                    protein = True
                if text.description in veggiefoods:
                    veggies = True
                if text.description in dairyfoods:
                    dairy = True
                if text.description in fruitfoods:
                    fruits = True
                if text.description in junkfoods:
                    junk = True
            for object in objects:
                if object.name in grainfoods:
                    grains = True
                if object.name in proteinfoods:
                    protein = True
                if object.name in veggiefoods:
                    veggies = True
                if object.name in dairyfoods:
                    dairy = True
                if object.name in fruitfoods:
                    fruits = True
                if object.name in junkfoods:
                    junk = True

            if fruits is True:
                contained.append('Fruits')
                stars += 1
            else:
                notcontained.append('Fruits')
            if grains is True:
                contained.append('Grains')
                stars += 1.5
            else:
                notcontained.append('Grains')
            if protein is True:
                contained.append('Protein')
                stars += 1
            else:
                notcontained.append('Protein')
            if veggies is True:
                contained.append('Vegetables')
                stars += 1
            else:
                notcontained.append('Vegetables')
            if dairy is True:
                contained.append('Dairy')
                stars += .5
            else:
                notcontained.append('Dairy')
            if junk is True:
                stars -= 1.5
                contained.append('Junk Food')
            else:
                notcontained.append('Junk Food')
            if stars < 0:
                stars = 0

            return render_template("upload_image.html", uploaded_image=im.filename, labels=labels, objects=objects, texts=texts, contained=contained, notcontained=notcontained, containlen=len(contained), notcontainlen=len(notcontained), stars=stars)


@app.route('/all', methods=['GET'])
def all():
    items = Images.query.all()
    items = [item.as_dict() for item in items]
    return jsonify(items)

@app.route('/store', methods=['POST'])
def store():
    data = request.get_json()
    uri = data["uri"]
    stars = data["stars"]
    image = Images(file_name=uri, stars=stars)
    db.session.add(image)
    db.session.commit()
    return("Successfully added image")

if __name__ == "__main__":
    app.run()
