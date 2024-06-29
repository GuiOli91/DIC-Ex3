import base64
import uuid
import cv2
import numpy as np
from flask import Flask, request, jsonify
import os

app = Flask(__name__)


net = cv2.dnn.readNet(os.path.join('yolo_tiny_configs', 'yolov3-tiny.weights'), 
                      os.path.join('yolo_tiny_configs', 'yolov3-tiny.cfg'))
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

@app.route('/api/object_detection', methods=['POST'])
def object_detection():
    data = request.json
    

    img_id = data.get('id', str(uuid.uuid4()))
    img_data = base64.b64decode(data['image_data'])

    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(confidence)
                class_ids.append(class_id)

    labels = []
    with open(os.path.join('yolo_tiny_configs', 'coco.names'), "r") as f:
        labels = [line.strip() for line in f.readlines()]

    detected_objects = []
    for i in range(len(boxes)):
        label = labels[class_ids[i]]
        accuracy = confidences[i] 
        detected_objects.append({
            "label": label,
            "accuracy": accuracy
        })

        x, y, w, h = boxes[i]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, f'{label} {accuracy:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    output_folder = 'out_folder'
    output_path = os.path.join(output_folder, f'{img_id}.jpg')
    cv2.imwrite(output_path, img)

    response = {
        "id": img_id,
        "objects": detected_objects
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
