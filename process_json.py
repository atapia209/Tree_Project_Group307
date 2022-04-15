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

if __name__ == "__main__": # TODO 
  with open(argv[1], "r") as aws_output_file:
    aws_output = json.load(aws_output_file)


  video_path = argv[2]
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



  for i, frame in enumerate(frames):
    # Pop up window showing the frame
    cv2.imshow(f"Frame {i}", frames[i])
    # Save the frame to images folder
    # TODO run a regex or something against the video's path so that we can include it in the name of the image, but ensure we don't catch any ../Folder parts
    cv2.imwrite(f"./images/{video_path}___Frame_{i}.jpg", frames[i])

  # wait for any key input
  cv2.waitKey(0)

  cv2.destroyAllWindows() 