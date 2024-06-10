import base64
import os
import requests
import argparse
import time

# Function to upload the images
def upload_images(image_name=None):

    # Specify the directory where images are located
    # images # object-detection-SMALL # object-detection-MEDIUM # object-detection-BIG
    image_dir = "./data/object-detection-BIG"

    # Get the list of all image files in the directory
    image_files = os.listdir(image_dir) if not image_name else [image_name]

    # Initialize variables to compute average inference time
    total_inf_time = 0
    total_upload_time = 0
    num_images = 0

    # Loop through each image file
    for image_file in image_files:
        if image_file in image_files:
            print(f"******** Processing image: {image_file} ********")

            # Open each image in read binary mode
            with open(os.path.join(image_dir, image_file), 'rb') as image:
                start_time = time.time()
                # Encode the binary data to base64 string
                base64_image = base64.b64encode(image.read()).decode('utf-8')

                # Specify the URL of the API endpoint
                # url = "http://localhost:5001/api/detect"
                # change DNS Public IPv4 DNS 'http: //[Public IPv4 DNS]:80/api/detect'
                url = "http://ec2-44-202-145-1.compute-1.amazonaws.com:80/api/detect"

                # Prepare the data to be sent to the API. This includes the encoded image.
                data = {"image": base64_image}

                # Make a POST request to the API endpoint with the prepared data
                response = requests.post(url, json=data)
                inf_time = float(response.json()['inf_time'])

                end_time = time.time()

                upload_time = end_time - start_time

                # Add the inference time to the total
                total_inf_time += inf_time
                total_upload_time += upload_time
                num_images += 1

                # Print out the response from the API
                print(response.json())
                print("Upload time:")
                print(upload_time)

    print("*****************************")
    print("Finished processing!")
    print("*****************************")
    print("Average inference time: ", total_inf_time / num_images)
    print("Average upload time: ", total_upload_time / num_images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload images for inference")
    parser.add_argument('-i', '--image', type=str, help="Name of a single image to process")
    args = parser.parse_args()
    upload_images(args.image)
