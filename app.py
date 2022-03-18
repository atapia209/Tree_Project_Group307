from flask import Flask, jsonify, request, session
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABSE_URI'] = 'postgresql+psycopg2://admin:password@localhost/virtualfarm'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'UCMBOB307'
db = SQLAlchemy(app)

#class Tree(db.Model):

#    __tablename__ = 'tree_specifications'
#    id = db.Column(db.Integer, primary_key = True)
#    tree_type = db.Column(db.Integer, nullable = False)
#   tree_width = db.Column(db.Integer, nullable = False)
    #Geolocation

#    def __repr__(self):
#        return "<Tree %r>" % self.id

@app.route('/')
def home():
    return "Front Page!"

#@cross_origin()
#@app.route('/data', methods = ['POST'])
#def create_tree():

#    tree_data = request.json

#    tree_type = tree_data['tree_type']
#    tree_width = tree_data['tree_width']

#    tree = Tree(tree_type = tree_type, tree_width = tree_width)
#    db.session.add(tree)
#    db.session.commit()

#    return jsonify({"success": True,"response":"Tree added"})

#@cross_origin()
#@app.route('/getdata', methods = ['GET'])
#def get_tree():

#    all_trees = []
#    tree_specifications = Tree.query.all()

#    for tree in tree_specifications:
#        results = {
#            "id":tree.id,
#            "tree_type":tree.tree_type,
#            "tree_width":tree.tree_width
#        }
#        all_trees.append(results)

#    return jsonify(
#        {
#            "success": True,
#            "tree_specifications": all_trees,
#            "total_trees": len(tree_specifications)
#        }
#    )

if __name__ == '__main__':
#    db.create_all()
    app.run(debug=True)