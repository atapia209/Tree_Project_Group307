import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

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
    return "Hello World"

#Run Servers
if __name__ == '__main__':
    app.run(debug=True)