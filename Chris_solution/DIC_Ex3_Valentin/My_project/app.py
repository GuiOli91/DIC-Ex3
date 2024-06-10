# Lint as: python3
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PIL import Image, ImageOps
# from PIL import ImageDraw
import os
# import detect
# import tflite_runtime.interpreter as tflite
# import platform
# import datetime
# import cv2
import time
import numpy as np
import io
# from io import BytesIO
from flask import Flask, request, Response, jsonify
# import random
import re
import tensorflow_hub as hub
import tensorflow as tf

UPLOADED_DATA_DIRECTORY = "uploaded_data"

# initializing the flask app
app = Flask(__name__)


def make_log(log):
    with open("results/inference_time_log.txt", "a+") as f:
        f.write(log)
    print(log)


def detection_loop(filename_image, path, output):
    # setting up a log
    make_log("START,detection of " + str(path) +
             "," + str(time.time())+"\n")

    total_time = 0
    output = {}
    for filename, _ in filename_image.items():

        # Loading the image and decoding it into a vector
        # image = ImageOps.fit(image, (256, 256), Image.ANTIALIAS)
        # image = image.convert("RGB")

        img = tf.io.read_file(os.path.join(path, filename))
        img = tf.image.decode_jpeg(img, channels=3)
        converted_img = tf.image.convert_image_dtype(img, tf.float32)[
            tf.newaxis, ...]

        # doing the actual item detection and timing
        start_time = time.time()
        result = detector(converted_img)

        # putting up results
        inference_time = time.time()-start_time  # time in s
        total_time += inference_time
        result = {key: value.numpy() for key, value in result.items()}
        # result consist of a dictionary with the following keys:
        # 'detection_class_entities', 'detection_class_labels', 'detection_scores',
        #'detection_boxes', 'detection_class_names'

        make_log("RESULTS," + filename + ", " + str(inference_time) + ", " +
                 np.array2string(result['detection_boxes']).replace('\n', '') + "\n")

        output[filename] = {"inference_time": inference_time, "detection_boxes": np.array2string(
            result['detection_boxes'])}

    make_log("FINAL RESULTS," + str(path) +
             "," + str(total_time)+"\n")

    output["total_time"] = total_time
    return output


@app.route('/api/detect', methods=['POST'])
# it is an endpoint to upload new images
def upload_images():
    filename = request.args["image_path"]
    os.makedirs(os.path.join(
        UPLOADED_DATA_DIRECTORY, os.path.dirname(filename)), exist_ok=True)

    img = request.files["image"].read()
    image = Image.open(io.BytesIO(img))
    image.save(os.path.join(UPLOADED_DATA_DIRECTORY,
                            filename), format="JPEG", quality=90)

    make_log("UPLOADED," + str(os.path.join(UPLOADED_DATA_DIRECTORY,
                                            filename)))

    return Response(status=200)


@app.route('/api/detect', methods=['GET'])
# it is an endpoint to detect new images
def detect():
    #img = request.files["image"].read()
    #image = Image.open(io.BytesIO(img))
    #data_input = request.args['input']
    data_input = request.values.get('input')
    output = request.values.get('output')
    #output = request.form.get('output')

    # data_input = "data/object-detection-SMALL/000000146462.jpg"
    path = data_input
    filename_image = {}

    input_format = ["jpg", "png", "jpeg"]
    if data_input.find(".") != -1:
        print(data_input + " is a file")
        split_data_input = data_input.split(".", 1)
        if data_input.endswith(tuple(input_format)):
            print("INPUT FORMAT: %s IS VALID" % split_data_input[1])
            path_splitted = []
            path_splitted = re.split('/', data_input)
            filename = path_splitted[len(path_splitted)-1]
            filename_image[filename] = Image.open(data_input)
            path = os.path.dirname(data_input)+"/"
    else:
        print(data_input + " is a path with the following files: ")
        for filename in os.listdir(data_input):
            image_path = data_input + filename
            filename_image[filename] = Image.open(image_path)
            print("  " + filename)

    output = detection_loop(filename_image, path, output)

    return jsonify(output)


# set up logging
os.makedirs("results", exist_ok=True)

make_log("APP START," + str(time.time()) + "\n")

# based on the Tensorflow tutorial (https://www.tensorflow.org/hub/tutorials/object_detection)
# downloading the TF module and setting up the model - may be worth changing the file to a local path to reduce comm cost
# module_handle = "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
module_handle = "./model"
detector = hub.load(module_handle).signatures['default']

make_log("LOADING THE MODEL FINISHED," + str(time.time()) + "\n")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5025)
