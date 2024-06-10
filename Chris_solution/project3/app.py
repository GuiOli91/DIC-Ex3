from PIL import Image
import time
import numpy as np
import io
from flask import Flask, request, Response, jsonify, make_response
import tensorflow_hub as hub
import base64
import tensorflow as tf

# Load the pre-trained model from TensorFlow Hub
# module_handle = "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
module_handle = 'https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1'
detector = hub.load(module_handle).signatures['default']

# Function to run inference for a single image
# in sample code referred to as: def detection_loop(filename_image):
def object_detection(image):
    # Convert the image to numpy array
    image = np.asarray(image)

    # Convert the image to tensor
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    # Start time of inference
    start_inf_time = time.time()

    # Perform inference
    output_dict = detector(input_tensor)
    result = output_dict

    # Calculate inference time
    inf_time = time.time() - start_inf_time

    # Convert tensors to numpy arrays
    result = {key: value.numpy() for key, value in result.items()}

    # Get number of objects detected
    num_objects_detected = len(result["detection_scores"])

    # Check if no objects are detected
    if num_objects_detected == 0:
        return None, inf_time
    else:
        return result, inf_time

# Initializing the flask app
app = Flask(__name__)

# Routing http posts to this method
@app.route('/api/detect', methods=['POST'])
def main():
    # Get data from request
    data= request.get_json(force = True)

    # Get the image from the json body
    img = data['image']

    # Open image and convert to numpy array
    image = Image.open(io.BytesIO(base64.b64decode(img)))
    # Convert black and white image to color (RGB)
    image = image.convert("RGB")
    image_np = np.array(image, dtype=np.float32)


    # Normalize pixel values to [0, 1]
    normalized_image_np = image_np / 255.0

    # Run detection for the image
    output_dict, inf_time = object_detection(normalized_image_np)

    # Get inference results
    bounding_boxes = []
    if output_dict is not None:
        bounding_boxes.extend(output_dict['detection_boxes'].tolist())

    # Prepare response data
    data = {
        "status": 200,
        "bounding_boxes": bounding_boxes,
        "inf_time": str(inf_time),
    }
    return make_response(jsonify(data), 200)

# Main driver function
if __name__ == '__main__':
    # Run the app
    app.run(debug = True, host = '0.0.0.0', port = 5001)
