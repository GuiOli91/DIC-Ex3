import requests
import os
import time

directory_to_upload = "data/object-detection-MEDIUM"
start_time = time.time()

for image in os.listdir(directory_to_upload):
    files = {
        'image': (image, open(os.path.join(directory_to_upload, image), 'rb'), 'image/jpg'),
    }

    # Where to upload
    upload_dest = "test_folder_medium"

    # locally
    # response = requests.post(
    #     'http://127.0.0.1:5000/api/detect?image_path=' + upload_dest + "/" + image, files=files)

    # to the cluster
    response = requests.post(
        'http://s25.lbd.hpc.tuwien.ac.at:5025/api/detect?image_path=' + upload_dest + "/" + image, files=files)

    print(response.status_code)

print("Total time to upload", time.time() - start_time)
