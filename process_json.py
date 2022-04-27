from concurrent.futures import process
import json
import cv2
from sys import argv


# Get the image from the vid_obj at the given timestamp
def getFromMS(video, timestamp):
  video.set(cv2.CAP_PROP_POS_MSEC, timestamp)
  _, image = video.read() # TODO don't use _, check to make sure it's  working
  return image

# Save the size of the video + set a scaled size (scaling unecessary)
def getSize(video):
  width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
  height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
  return (width, height)


def drawRectangle(image, bounding_box, width, height):  
  start_point = (int(bounding_box["Left"] * width), int(bounding_box["Top"] * height))
  end_point = (int(start_point[0] + bounding_box["Width"] * width), int(start_point[1] + bounding_box["Height"] * height))
  
  color = (0,0,255)
  thickness = 5

  return cv2.rectangle(image, start_point, end_point, color, thickness)

def scaleImage(image, scale, width, height):
  return cv2.resize(image, (int(width * scale), int(height * scale)), interpolation = cv2.INTER_LINEAR)
  
def cropImage(image, bounding_box, width, height):
  # Crop the image
  height = len(image)
  width = len(image[0])
  start_point = (int(bounding_box["Left"] * width), int(bounding_box["Top"] * height))
  end_point = (int(start_point[0] + bounding_box["Width"] * width), int(start_point[1] + bounding_box["Height"] * height))
  return image[start_point[1]:end_point[1], start_point[0]:end_point[0]]


def processJSON(json_path, video_path, name = "", counter = 0):
  with open(json_path, "r") as aws_output_file:
    aws_output = json.load(aws_output_file)

  if(len(name) == 0):
    name = video_path
  
  vid_obj = cv2.VideoCapture(video_path)
  frames = []

  for i, detection in enumerate(aws_output):
    (width, height) = getSize(vid_obj)

    still = getFromMS(vid_obj, detection["Timestamp"])


    # Draw the rectangle
    bounding_box = detection["Geometry"]["BoundingBox"]
    still = drawRectangle(still, bounding_box, width, height)

    # crop the image
    # still = cropImage(still, detection["Geometry"]["BoundingBox"], width, height)

    # # Resize the image
    still = scaleImage(still, 0.25, width, height)

    # Add the image to our list of images
    frames.append(still)

  handleImages(frames, "./images", name, counter)

  # Returns this so if we're processing multiple videos for the same portion we can keep the counter/name consistent between them
  return len(frames)
  
def handleImages(imgs, location, name, counter):
  # print(len(imgs))
  for i, frame in enumerate(imgs):
    # Pop up window showing the frame
    cv2.imshow(f"Frame {i + counter}", imgs[i])
    # Save the frame to images folder
    cv2.imwrite(f"{location}/{name}_{i+counter}.jpg", imgs[i])

def processMultiple(json_paths, video_paths, name):
  counter = 0
  for i, path in enumerate(json_paths):
    counter += processJSON(path, video_paths[i], name, counter)


if __name__ == "__main__": # TODO 
  json_paths = argv[1::2]
  video_paths = argv[2::2]
  
  processMultiple(json_paths, video_paths, "TEST")

  # wait for any key input
  cv2.waitKey(0)

  cv2.destroyAllWindows() 