import json
import boto3
import base64
import uuid
import cv2
import numpy as np
import os
from decimal import Decimal

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    print(event)


    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    tmp_file = f"/tmp/{key.split('/')[-1]}"
    
    # Download image from S3
    s3.download_file(bucket, key, tmp_file)
    
    # Load YOLO configs files from the bucket
    ## objects names
    s3.download_file(bucket, "yolo_tiny_configs/coco.names", "/tmp/coco.names")
    # model config
    s3.download_file(bucket, "yolo_tiny_configs/yolov3-tiny.cfg", "/tmp/yolov3-tiny.cfg")
    # model weights
    s3.download_file(bucket, "yolo_tiny_configs/yolov3-tiny.weights", "/tmp/yolov3-tiny.weights")
    
    
    # Load YOLO model
    net = cv2.dnn.readNet('/tmp/yolov3-tiny.weights', '/tmp/yolov3-tiny.cfg')
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Load image
    img = cv2.imread(tmp_file)
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    
    # NOTE: The following code is kept to be comparable with the local execution
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
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    labels = []
    with open('/tmp/coco.names', "r") as f:
        labels = [line.strip() for line in f.readlines()]
    
    detected_objects = []
    for i in range(len(boxes)):
        label = labels[class_ids[i]]
        accuracy = Decimal(str(confidences[i]))
        detected_objects.append({
            "label": label,
            "accuracy": accuracy
        })
        
        # Draw bounding box and label on the image
        x, y, w, h = boxes[i]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, f'{label} {accuracy:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Upload result to S3
    result_key = f"results/detected_{key.split('/')[-1]}"

    
    # Prepare data for DynamoDB
    table = dynamodb.Table('ObjectDetectionResults')
    response = table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            's3_url': f"s3://{bucket}/{result_key}",
            'objects': detected_objects
        }
    )
    
    # Log the output
    print(f"Image processed and uploaded to: s3://{bucket}/{result_key}")
    print(f"DynamoDB entry created with ID: {response['ResponseMetadata']['RequestId']}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Object detection complete', 'output': result_key})
    }
