#Build docker image from Dockerfile
docker build -t object-detection-app .

# Run docker container locally
docker run -p 5001:5001 object-detection-app

# Run docker on AWS EC2 instance
docker run -p 80:5001 –name dic_ex3 bettinaroe/dic_ex3:latest

