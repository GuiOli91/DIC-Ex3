import boto3
import os


def hello_s3():
    """
    Use the AWS SDK for Python (Boto3) to create an Amazon Simple Storage Service
    (Amazon S3) resource and list the buckets in your account.
    This example uses the default settings specified in your shared credentials
    and config files.
    """
    s3_resource = boto3.resource("s3")
    print("Hello, Amazon S3! Let's list your buckets:")
    for bucket in s3_resource.buckets.all():
        print(f"\t{bucket.name}")
        return bucket
        
def upload_image(bucket):
    
    s3_client = boto3.client("s3")
    folder_path = "/home/guilherme/Projects/TuW/data_intensive/DIC-Ex3/input_folder"  # Replace with the actual path to your folder

    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg"):
            image_path = os.path.join(folder_path, filename)
            image_name = filename
            try:
                s3_client.upload_file(image_path, bucket.name, image_name)
                print(f"Image {image_name} uploaded successfully to bucket: {bucket.name}")
            except Exception as e:
                print(f"Error uploading image to bucket: {bucket.name}")
                print(e)
                

        
        
        

if __name__ == "__main__":
    bucket = hello_s3()
    upload_image(bucket)