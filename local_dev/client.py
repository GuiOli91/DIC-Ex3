import argparse
import cv2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = "client",
        description=" This script receives a folder with jpegs images processes \
        them and send the results to an API. And may save them to a folder.")
    parser.add_argument('folder', help='Folder with images to process')
    parser.add_argument('API_URL', help='API URL to send the results')
    parser.add_argument('--save', help='Save the results to a folder')

    args = parser.parse_args()
    print('oi')
# print(args.accumulate(args.integers))