from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Accel_54@localhost/virtualOrchard'

db = SQLAlchemy(app)

class trees(db.Model):

    __tablename__ = 'trees'
    id = db.Column(db.Integer(), primary_key = True)
    width = db.Column(db.Integer(), nullable = False, default = 0)
    #Geolocation

    def __init__(self, id, width):
        self.id = id
        self.width = width
#        return "<Tree %r>" % self.id

db.create_all()

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")

@app.route('/test')
def test():
    return {
        'test': 'test'
    }

#@cross_origin()
@app.route('/trees', methods = ['GET'])
def gtree():

    tree_spec = trees.query.all()
    all_trees = []

    for tree in tree_spec:
        current_tree = {}
        current_tree['id'] = tree.id
        current_tree['width'] = tree.width
        all_trees.append(current_tree)

    return jsonify(all_trees)

#@cross_origin()
@app.route('/trees', methods = ['POST'])
def ctree():

    tree_data = request.get_json()
    tree = trees(id = tree_data['id'], width = tree_data['width'])
    db.session.add(tree)
    db.session.commit()

    return jsonify(tree_data)

if __name__ == '__main__':
    app.run(debug=True)