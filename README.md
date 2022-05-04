# Tree_Project_Group307 (Tree2Tree)

Gemperle Family Farms is a family owned and operated farm, currently relying on manual labor to count and locate planted trees after the delivery from a nursery.  Team Tree2Tree was tasked with automating the process to reduce labor costs and increase accuracy. We developed a vision based system utilizing Amazon Rekognition and built a machine learning model that detects trees by training labels. The software will be able to count and display tree data accordingly. This information can then be presented on our interactive web application which displays the count and relative location to each other on a simulated map.

## Installation

Information linked provides a set up tutorial on VS Code to run a Flask environment.
https://code.visualstudio.com/docs/python/tutorial-flask

Information to install opencv-python. Required to run specific data and images processes in the background of the detection.
https://pypi.org/project/opencv-python/

Use the package manager pip to install install the required packages and dependencies.

AWS CLI Install (latest version)

```python
  pip3 install awscli --upgrade --user
```
```
  aws configure
```

* You will be prompted to enter your access key, secret key. The region should be set to us-region-2 and format to JSON *

Requirements.txt Install
```
  pip3 install -r requirements.txt
```
## Running the Model

For AWS Rekognition, refer to https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/gs-step-start-model.html

Starting the model

<img width="460" alt="image" src="https://user-images.githubusercontent.com/69406340/166725486-10381288-af46-49ca-9e3a-3f25ecdde8f7.png">

Stopping the model

<img width="460" alt="image" src="https://user-images.githubusercontent.com/69406340/166725359-818da278-8b6e-4979-bc6f-e22356f4e49c.png">

## Running the Flask Application

Once model is running. In the command line run the flask application:
```
  flask run
```
*Note* Remember to turn off the model when application is offline.

If your's a first time user, register an account using the specified page. Once signed in refer to our demo below:

* Notes *
Uploaded files must be of .mp4 format, the size of the files is not limited but will increase wait time for the model to return results.
