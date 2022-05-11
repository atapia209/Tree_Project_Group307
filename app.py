import os
import time

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
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

# Initialze file upload
upload_folder = os.path.join(maindir, 'uploads')
allowed_extensions = {'mp4'}

if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

app.config['UPLOAD_FOLDER'] = upload_folder

# file upload validation
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

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

# File Main Model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(30), nullable=False, unique=False)

    def __init__(self, filename):
        self.filename = filename + time.strftime("%y%m%d%H%M%S")

# File Schema
class FileSchema(ma.Schema):
    class Meta:
        fields = ('id','filename')

file_schema = FileSchema()
files_schema = FileSchema(many=True)

# admin model view
class MyModelView(ModelView):

    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Admin
admin = Admin(app, name='Admin', template_mode='bootstrap3')
admin.add_view(MyModelView(User, db.session, name='Users'))
admin.add_view(MyModelView(Tree, db.session, name='Tree'))
admin.add_view(MyModelView(File, db.session, name='Files'))
#admin.add_view(MyModelView(File, db.session, name='Quit'))

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

@app.route('/trees', methods=['POST'])
def add_tree(row_json, column_json, confidence_json):
    row = row_json
    column = column_json
    confidence = confidence_json

    new_tree = Tree(row, column, confidence)

    db.session.add(new_tree)
    db.session.commit()

    return tree_schema.jsonify(new_tree)

@app.route('/trees', methods=['GET'])
@cross_origin()
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

@app.route('/trees', methods=['DELETE'])
def delete_all_trees():
    all_trees = Tree.query.all()
    for tree in all_trees:
        db.session.delete(tree)
    db.session.commit()
    
    return trees_schema.jsonify(all_trees)

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

@app.route('/upload', methods=['GET', 'POST', 'DELETE'])
@login_required
def upload():

    if request.method == 'POST':
        
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        # if user selects incorrect file type
        if files[0].filename.split('.')[1] != 'mp4':
            flash('Incorrect file type')
        
        # if user selects a file that already exists
        # if File.query.filter_by(filename=files[0].filename).first():
        #     flash('File already exists')
        #     return redirect(request.url)

        for file in files:
            print(files[0].filename)
            print(files[1].filename)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                Detect_trees_in_video(filename)
                print("./uploads/"+ filename)
                # Add file to database
                new_file = File(filename)
                db.session.add(new_file)
                db.session.commit()

            flash('File(s) uploaded successfully')
            #process_json_info()
        return redirect(url_for('upload'))

    return render_template('upload.html')


    # delete all files
    if request.method == 'DELETE':
        for file in files:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            db.session.delete(file)
            db.session.commit()
        flash('File(s) deleted successfully')
        return redirect(url_for('upload'))    

    return render_template('upload.html')

    # get all files
    if request.method == 'GET':
        all_files = File.query.all()
        result = files_schema.dump(all_files)
        return jsonify(result)

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
    Detect_trees_in_video(f"./uploads/1.mp4")
    #files is array/list
    #file is individual file

    #files = request.files.getlist('files[]')

    # for file in files:
    #     #filename = 
    #     Detect_trees_in_video(file.filename)
    # #Detect_trees_in_video("Tree_vid_1.mp4")

    #list = os.listdir("C:/Users/alann/.vscode/Python_Workspace\Python/Tree_Final/uploads") # dir is your directory path
    #number_files = len(list)
    

    #for i in range(number_files):
        #Detect_trees_in_video(f"./uploads/{i+1}.mp4")
        
        
    return redirect(url_for('load'))

@app.route('/scan_second_video/')
def scan_second_video():
    Detect_trees_in_video("Tree_vid_2.mp4")
    return redirect(url_for('load'))

@app.route('/scan_third_video/')
def scan_third_video():
    #Detect_trees_in_video("Tree_vid_3.mp4")
    delete_all_trees()
    return redirect(url_for('load'))

@app.route('/process_json_info/')
def process_json_info():
    # current_row = 0
    # current_tree_count = 0
    # #Counts and organizes rows and columns in Tree_Table[], and Trees[]
    # #current_row,current_tree_count = json_process("Tree_vid_1.mp4.json",current_row,current_tree_count)
    # #current_row,current_tree_count = json_process("Tree_vid_2.mp4.json",current_row,current_tree_count)
    # #current_row,current_tree_count = json_process("Tree_vid_3.mp4.json",current_row,current_tree_count)
    # #for i in range()
    # list = os.listdir("C:/Users/alann/.vscode/Python_Workspace\Python/Tree_Final/uploads") # dir is your directory path
    # number_files = len(list)
    # for i in range(number_files):
    #     #Detect_trees_in_video(f"./uploads/{i+1}.mp4")
    #     current_row,current_tree_count = json_process(f"./uploads/{i+1}.mp4.json",current_row,current_tree_count)
    json_process()
    adding_tree_final_draft()
    last_step()
    return redirect(url_for('dashboard'))

@app.route('/Display_Tree_Table/')
def Display_Tree_Table():
    Print_Tree_Table()
    return redirect(url_for('load'))
##########################################################################################################################
#Definitions

def json_process():
    # json_file = open(json_file_name)
    # data = json.loads(json_file.read())
    # count = 0
    # current_confidence = 0
    # for index, sub_data in enumerate(data):
    #     #print("index:" , index, "Stuff inside sub_data: ", sub_data, "\nType:", sub_data['Name'])
    #     Trees.append([current_tree_count + index, sub_data['Name'], sub_data['Confidence'], sub_data['Geometry']])
    #     count +=1
    # print('There were', count, " trees detected in row: ", current_row," in Video: ",  json_file_name)
    # Tree_table_list.append([count])
    # #Tree_table_list.append(count)

    list = os.listdir("./uploads") # dir is your directory path
    number_files = len(list)
    for i in range(number_files):
        #Detect_trees_in_video(f"./uploads/{i+1}.mp4")
        #current_row,current_tree_count = json_process(f"./uploads/{i+1}.mp4.json",current_row,current_tree_count)

        json_file = open(f"{i+1}.mp4.json")
        data = json.loads(json_file.read())

        count = len(data)
        temp = 0

        for index, sub_data in enumerate(data):
            #print( "Label: " , data[count]['Name'])
            #print("Confidence: ", data[count]['Confidence'])
            if index == 0:
                Trees.append([data[index]['Name'], data[index]['Confidence'], data[index]['Geometry']['BoundingBox'], data[index]['Timestamp']])
            elif index > 0 and index < count:
                #print(data[index]['Timestamp'], " - ",data[index-1]['Timestamp'], " == " , data[index]['Timestamp'] - data[index-1]['Timestamp'])
                if data[index]['Timestamp'] - data[index-1]['Timestamp'] == 1000:
                    print("Will not be adding this tree, these trees are two close together")
                else:
                    Trees.append([data[index]['Name'], data[index]['Confidence'], data[index]['Geometry']['BoundingBox'], data[index]['Timestamp']])
                    temp = temp + 1

        print("Done with ",f"{i+1}.mp4.json", "| temp:", temp)   
        Tree_table_list.append(temp +1)

def adding_tree_final_draft():
    total_index = 0
    for i, row_length in enumerate(Tree_table_list):
        for j in range(row_length):
            add_tree(i,j,Trees[j + total_index][1])
        total_index += row_length


def Print_Tree_Table():
    for i in range(len(Tree_table_list)):
        print("Current Row:", i, "| Number of Trees in Row:",Tree_table_list[i])
    # print(Tree_table_list)
    for i in range(len(Trees)):
        print("Tree Index: ", i, "| Type:", Trees[i][0], "| Confidence: ",Trees[i][1],"| Geometry: ", Trees[i][2], "|Timestamp: ", Trees[i][3])
        #also has Gemotry for bounding boxes saved in [i][3] = 'Geomtry' but user doesn't need to 
        #see that

def Detect_trees_in_video(video_name):

    print(" Inside Detect_trees_in_video()")
    videoFile = "./uploads/" + video_name
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
        #Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
        #PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)
    
    print(customLabels)

    newjson_name = (video_name + ".json")

    with open(newjson_name, "w") as f:
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

def last_step():
  tree_count = 0
  list = os.listdir("./uploads") # dir is your directory path
  number_files = len(list)
  for index in range(number_files):
      #Detect_trees_in_video(f"./uploads/{i+1}.mp4")
      #current_row,current_tree_count = json_process(f"./uploads/{i+1}.mp4.json",current_row,current_tree_count)

    #json_file = open(f"{index+1}.mp4.json")
    #aws_output = json.loads(json_file.read())
    aws_output = Trees

   # with open('Tree_vid_1.mp4.json') as aws_output_file:
      #aws_output = json.load(aws_output_file)

   #video_path = argv[2]
    video_path = f"./uploads/{index+1}.mp4"
    vid_obj = cv2.VideoCapture(video_path)
    frames = []

    #for i, detection in enumerate(aws_output):
    for i, detection in enumerate(range(Tree_table_list[index])):
      (width, height) = getSize(vid_obj)

      still = getFromMS(vid_obj, Trees[i][3])

      # Draw the rectangle
      bounding_box = Trees[i][2]
      still = drawRectangle(still, bounding_box, width, height)

      # # Resize the image
      still = scaleImage(still, 0.25, width, height)

      # Add the image to our list of images
      frames.append(still)

    for i, frame in enumerate(frames):
      # Pop up window showing the frame
      #cv2.imshow(f"Frame {i}", frames[i])
      # Save the frame to images folder
      # TODO run a regex or something against the video's path so that we can include it in the name of the image, but ensure we don't catch any ../Folder parts
      cv2.imwrite(f"./detected_images/Index.{tree_count}.Row.{index}.Column.{i}.jpg", frames[i])
      tree_count = tree_count + 1
    # wait for any key input
    #cv2.waitKey(0)

    cv2.destroyAllWindows()

#Run Servers
if __name__ == '__main__':
    app.run(debug=True)
