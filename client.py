import requests
import base64
import os
import uuid
import sys

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main(input_folder, endpoint):
    for image_filename in os.listdir(input_folder):
        image_path = os.path.join(input_folder, image_filename)
        encoded_image = encode_image(image_path)
        image_id = str(uuid.uuid4())
        payload = {
            "id": image_id,
            "image_data": encoded_image
        }
        response = requests.post(endpoint, json=payload)
        print(response.json())

if __name__ == "__main__":
    input_folder = sys.argv[1]
    endpoint = sys.argv[2]
    main(input_folder, endpoint)
