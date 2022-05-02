import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

#Alann
import json
import boto3
import cv2
import math
import io
import cv2
from sys import argv

#Tree_table_list = [current_row ,columns = total size = count], [current_row + 1, number of trees in row2] ]
Tree_table_list = []
Trees = []
#current_row = 0

# Initialize the app
app = Flask(__name__)
maindir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(maindir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Initialize marshmallow
ma = Marshmallow(app)

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Main Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=15)])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=15)])

    submit = SubmitField('Sign In')

# Tree Main Model
class Tree(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.Integer, unique=False)
    column = db.Column(db.Integer, unique=False)
    confidence = db.Column(db.Float, unique=False)

    def __init__(self, row, column, confidence):
        self.row = row
        self.column = column
        self.confidence = confidence

# Tree Schema
class TreeSchema(ma.Schema):
    class Meta:
        fields = ('id','row', 'column', 'confidence')

tree_schema = TreeSchema()
trees_schema = TreeSchema(many=True)

@app.route('/trees', methods=['POST'])
def add_tree():
    row = request.json['row']
    column = request.json['column']
    confidence = request.json['confidence']

    new_tree = Tree(row, column, confidence)

    db.session.add(new_tree)
    db.session.commit()

    return tree_schema.jsonify(new_tree)

@app.route('/trees', methods=['GET'])
def get_trees():
    all_trees = Tree.query.all()
    result = trees_schema.dump(all_trees)
    return jsonify(result)

@app.route('/trees/<id>', methods=['DELETE'])
def delete_tree(id):
    tree = Tree.query.get(id)
    db.session.delete(tree)
    db.session.commit()

    return tree_schema.jsonify(tree)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('upload'))

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('login-1.html', form=form)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    return render_template('upload.html')

@app.route('/load')
@login_required
def load():
    return render_template('load.html')

#Route for dashboard Uncomment when dashboard is ready
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/scan_first_video/')
def scan_first_video():
    Detect_trees_in_video("Tree_vid_1.mp4")
    return redirect(url_for('load'))

@app.route('/scan_second_video/')
def scan_second_video():
    Detect_trees_in_video("Tree_vid_2.mp4")
    return redirect(url_for('load'))

@app.route('/scan_third_video/')
def scan_third_video():
    Detect_trees_in_video("Tree_vid_3.mp4")
    return redirect(url_for('load'))

@app.route('/process_json_info/')
def process_json_info():
    current_row = 0
    current_tree_count = 0
    #Counts and organizes rows and columns in Tree_Table[], and Trees[]
    current_row,current_tree_count = json_process("Tree_vid_1.mp4.json",current_row,current_tree_count)
    current_row,current_tree_count = json_process("Tree_vid_2.mp4.json",current_row,current_tree_count)
    current_row,current_tree_count = json_process("Tree_vid_3.mp4.json",current_row,current_tree_count)
    #Resets tree count in order to rename images 0-41 again
    #current_tree_count = 0
    #current_tree_count = Draw_BB_on_Images_N_Save("Tree_vid_1.mp4", "Tree_vid_1.mp4.json",current_tree_count)
    #current_tree_count = Draw_BB_on_Images_N_Save("Tree_vid_2.mp4", "Tree_vid_2.mp4.json",current_tree_count)
    #current_tree_count = Draw_BB_on_Images_N_Save("Tree_vid_3.mp4", "Tree_vid_3.mp4.json",current_tree_count)

    return redirect(url_for('load'))

@app.route('/Display_Tree_Table/')
def Display_Tree_Table():
    Print_Tree_Table()
    return redirect(url_for('load'))
#################################################################################
#Definitions

def json_process(json_file_name,current_row,current_tree_count):
    json_file = open(json_file_name)
    data = json.loads(json_file.read())
    count = 0
    current_confidence = 0
    for index, sub_data in enumerate(data):
        #print("index:" , index, "Stuff inside sub_data: ", sub_data, "\nType:", sub_data['Name'])
        Trees.append([current_tree_count + index, sub_data['Name'], sub_data['Confidence'], sub_data['Geometry']])
        count +=1
    print('There were', count, " trees detected in row: ", current_row," in Video: ",  json_file_name)
    Tree_table_list.append([current_row,count])
    #Tree_table_list.append(count)
    return current_row + 1, current_tree_count + count

def Print_Tree_Table():
    for i in range(len(Tree_table_list)):
        print("Current Row:", Tree_table_list[i][0], "| Number of Trees in Row:",Tree_table_list[i][1])
    print(Tree_table_list)
    for i in range(len(Trees)):
        print(" Tree Index:", Trees[i][0], "| Type: ",Trees[i][1],"| Confidence: ", Trees[i][2])
        #also has Gemotry for bounding boxes saved in [i][3] = 'Geomtry' but user doesn't need to 
        #see that

def Detect_trees_in_video(video_name):
    videoFile = video_name
    projectVersionArn = "arn:aws:rekognition:us-east-2:520310994707:project/Tree_Detect_v5/version/Tree_Detect_v5.2022-04-16T07.46.59/1650120417223"
    rekognition = boto3.client('rekognition')        
    customLabels = []    
    cap = cv2.VideoCapture(videoFile)
    frameRate = cap.get(5) #frame rate
    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        print("Processing frame id: {}".format(frameId))
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % math.floor(frameRate) == 0):
            hasFrame, imageBytes = cv2.imencode(".jpg", frame)

            if(hasFrame):
                response = rekognition.detect_custom_labels(
                    Image={
                        'Bytes': imageBytes.tobytes(),
                    },
                    ProjectVersionArn = projectVersionArn
                )
            
            for elabel in response["CustomLabels"]:
                elabel["Timestamp"] = (frameId/frameRate)*1000
                customLabels.append(elabel)
    
    print(customLabels)

    with open(videoFile + ".json", "w") as f:
        f.write(json.dumps(customLabels)) 

    cap.release()
    print ('Function Completed...\nJSON Created for ',video_name,'.')

def Detect_trees_in_second_video():
    print ('Function Activated, Scanning Second Video...\nDone.')

def Detect_trees_in_third_video():
    print ('Function Activated, Scanning Third Video...\nDone.')

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

def Draw_BB_on_Images_N_Save(Video_Path_String, JSON_Path,current_tree_count_local):
    with open(JSON_Path) as aws_output_file:
        aws_output = json.load(aws_output_file)

    video_path = Video_Path_String
    vid_obj = cv2.VideoCapture(video_path)
    frames = []

    for i, detection in enumerate(aws_output):
        (width, height) = getSize(vid_obj)

        still = getFromMS(vid_obj, detection["Timestamp"])

    # Draw the rectangle
    bounding_box = detection["Geometry"]["BoundingBox"]
    still = drawRectangle(still, bounding_box, width, height)

    # Resize the image
    still = scaleImage(still, 0.25, width, height)
    # Add the image to our list of images
    frames.append(still)

    for i, frame in enumerate(frames):
        # Pop up window showing the frame
        #cv2.imshow(f"Frame {i}", frames[i])
        # Save the frame to images folder
        # TODO run a regex or something against the video's path so that we can include it in the name of the image, but ensure we don't catch any ../Folder parts
        current_tree_count_local = current_tree_count_local + i
        cv2.imwrite(f"./images/{current_tree_count_local}.jpg", frames[i])

    # wait for any key input
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return current_tree_count_local

#Run Servers
if __name__ == '__main__':
    app.run(debug=True)
