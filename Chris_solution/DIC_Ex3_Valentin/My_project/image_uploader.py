import requests
import os
import time

directory_to_upload = "/Users/valentin/Documents/TU Wien/Data-Intensive-Computing/ex3/datasets/OneDrive_1_6-13-2022/object-detection-MEDIUM"
start_time = time.time()

for image in os.listdir(directory_to_upload):
    files = {
        'image': (image, open(os.path.join(directory_to_upload, image), 'rb'), 'image/jpg'),
    }

    # Where to upload
    upload_dest = "test_folder"

    response = requests.post(
         'http://127.0.0.1:5025/api/detect?image_path=' + upload_dest + "/" + image, files=files)
    #response = requests.post(
    #    'http://s25.lbd.hpc.tuwien.ac.at:5025/api/detect?image_path=' + upload_dest + "/" + image, files=files)
    print(response.status_code)

print("Total time to upload", time.time() - start_time)
