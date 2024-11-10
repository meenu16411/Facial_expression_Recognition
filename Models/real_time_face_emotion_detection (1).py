# -*- coding: utf-8 -*-
"""REAL TIME FACE  EMOTION DETECTION

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/122zLvuw6tsr-d3Xi2TtxbP8zZtRwWQlH

Import required Python libraries
"""

import imutils
import numpy as np
import cv2
import dlib
from google.colab.patches import cv2_imshow
from IPython.display import display, Javascript
from google.colab.output import eval_js
from base64 import b64decode
from imutils import face_utils

from google.colab import drive
drive.mount("/content/gdrive")

"""Start webcam"""

def take_photo(filename='photo.jpg', quality=0.8):
  js = Javascript('''
    async function takePhoto(quality) {
      const div = document.createElement('div');
      const capture = document.createElement('button');
      capture.textContent = 'Capture';
      div.appendChild(capture);

      const video = document.createElement('video');
      video.style.display = 'block';
      const stream = await navigator.mediaDevices.getUserMedia({video: true});

      document.body.appendChild(div);
      div.appendChild(video);
      video.srcObject = stream;
      await video.play();

      // Resize the output to fit the video element.
      google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

      // Wait for Capture to be clicked.
      await new Promise((resolve) => capture.onclick = resolve);

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      stream.getVideoTracks()[0].stop();
      div.remove();
      return canvas.toDataURL('image/jpeg', quality);
    }
    ''')
  display(js)
  data = eval_js('takePhoto({})'.format(quality))
  binary = b64decode(data.split(',')[1])
  with open(filename, 'wb') as f:
    f.write(binary)
  return filename

"""Click 'Capture' to make photo using your webcam."""

image_file = take_photo()

"""Read, resize and display the image."""

#image = cv2.imread(image_file, cv2.IMREAD_UNCHANGED)
image = cv2.imread(image_file)

# resize it to have a maximum width of 400 pixels
image = imutils.resize(image, width=400)
(h, w) = image.shape[:2]
print(w,h)
cv2_imshow(image)

gray_image =cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
face_cascade =cv2.CascadeClassifier("/content/gdrive/MyDrive/frontal_face")
face =face_cascade.detectMultiScale(gray_image,1.1,5)

"""Load the pre-trained face detection network model from disk"""

print("[INFO] loading model...")
prototxt = '/content/gdrive/MyDrive/deploy.prototxt.txt'
model = '/content/gdrive/MyDrive/res10_300x300_ssd_iter_140000.caffemodel'
net = cv2.dnn.readNetFromCaffe(prototxt, model)

"""Use the [dnn.blobFromImage](https://www.pyimagesearch.com/2017/11/06/deep-learning-opencvs-blobfromimage-works/) function to construct an input blob by resizing the image to a fixed 300x300 pixels and then normalizing it.

"""

# resize it to have a maximum width of 400 pixels
image = imutils.resize(image, width=400)
blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

"""
Pass the blob through the neural network and obtain the detections and predictions."""

print("[INFO] computing object detections...")
net.setInput(blob)
detections = net.forward()
detections.shape[2]

from tensorflow import keras  # Import keras from tensorflow
from tensorflow.keras.models import Sequential, model_from_json #add Sequential import here

#load model for predictions
import tensorflow as tf # Import tensorflow as tf

# Import necessary modules
from tensorflow import keras
from tensorflow.keras.models import Sequential, model_from_json

json_file = open('/content/gdrive/MyDrive/model.json','r')
loaded_model_json=json_file.read()
json_file.close()

# Load the model using model_from_json
loaded_model = model_from_json(loaded_model_json, custom_objects={'Sequential': tf.keras.models.Sequential})

#loading weights of model
loaded_model.load_weights("/content/gdrive/MyDrive/model.h5")
print("model loaded suceesfully")

emotion_classifier =loaded_model
emotions = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

from google.colab.patches import cv2_imshow
# Loop over the detections and draw boxes around the detected faces
for i in range(0, detections.shape[2]):
    # extract the confidence (i.e., probability) associated with the prediction
    confidence = detections[0, 0, i, 2]

    # filter out weak detections by ensuring the `confidence` is greater than the minimum confidence threshold
    if confidence > 0.5:
        # compute the (x, y)-coordinates of the bounding box for the object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")

        # extract the face region from the image
        face_roi = image[startY:endY, startX:endX]

        # preprocess the face region for the emotion classifier
        face_roi = cv2.resize(face_roi, (48, 48))
        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        face_roi = face_roi.astype("float") / 255.0
        face_roi = np.reshape(face_roi, (1, 48, 48, 1))

        # use the loaded emotion classifier to predict the emotion
        emotion_probabilities = emotion_classifier.predict(face_roi)[0]
        emotion_label = np.argmax(emotion_probabilities)
        emotion_text = emotions[emotion_label]

        # draw the bounding box of the face along with the associated emotion
        text = "{}: {:.2f}%".format(emotion_text, confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.putText(image, text, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

# Show the resulting image
cv2_imshow(image)