from flask import Flask, request, jsonify
from flask_restful import Api, Resource

from pymongo import MongoClient

import bcrypt

import numpy as np

import requests
import keras

import tensorflow as tf


from keras.applications.inception_v3 import InceptionV3

from keras.applications.inception_v3 import preprocess_input

from keras.applications import imagenet_utils # utils Imports utlities for working with models trained on Imagellet 
#Also helps us to decode the model predictions. Converting model prediction result to human readable format

from tensorflow.keras.preprocessing.image import img_to_array
# Converting inage to numpy array, which can be given as Input to the deep learning nodel

from PIL import Image # For resize, open and work with Images

from io import BytesIO # This class provides file like interface for raw byte data We are going to convert the content of an image received from the Http response into a stream that can be used as an input to PIL's imagee class.

app =Flask(__name__) 
api =Api(app)

#Load the pretrained model

pretrained_model =InceptionV3(weights ="imagenet")

#Initialising Mongo Client with port

client=MongoClient("mongodb://db:27017")

#creating a new De and collection as well
db= client.ImageRecognition
users= db["users"]



def user_exists(username):
    if users.count_documents ({"Username":username})==0:

        return False

    else:
       return True

class Register (Resource):
   def post (self):

    #we first get the posted data

    posted_data =request.get_json()

    #Get user name and password

    username =posted_data["username"] 
    password =posted_data["password"]

    #Check if user already exist

    if user_exists(username):

     return jsonify ({

        "status":301, "message": "Invalid username, user already exist" })

    #if user is new hash the password
    hashed_pw= bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

    #After password hashed we will store the password in database

    users.insert_one({

    "Username":username,

    "Password": hashed_pw,

    "Tokens":4

    })

    #Resturn Sucess

    ret_json={
      
    "status":200,

    "message": "You have successfully signed up for the API "
    }

    

    return jsonify (ret_json)

api.add_resource(Register, '/register')

class Classify(Resource):

    def post(self):

        #Get Posted data

        posted_data= request.get_json()

        #We get Credentials and URL 
        username =posted_data['username']

        password= posted_data['password']

        url=posted_data['url']

        # #Verify the Credentials
        ret_json, error =verify_credentials(username, password) 
        #if verification failes, error is True

        if error:
            return jsonify(ret_json)

        # #check if user have tokens

        tokens =users.find({
             "Username": username })[0]["Tokens"]

        if tokens <0:
            return jsonify(generate_return_dictionary(303, "Not have Enough Tokens"))

        if not url:
            return jsonify (({ "message": "No URL Provided" }), 400)

        # #Load Image from URL

        response= requests.get(url)

        img= Image.open(BytesIO(response.content))

        #Preprocess the image for making suitable for InceptionV3 Model

        img=img.resize (299, 299)

        img_array =img_to_array(img)

        img_array= np.expand_dims(img_array, axis=0)

        img_array =preprocess_input(img_array)

        