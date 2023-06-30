from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from details import API_KEY
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


# since GET is allowed by default
# we don't have to write down methods='GET'
@app.route('/random')
def random_cafe():
    if request.method == "GET":
        cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(cafes).__dict__
        del random_cafe['_sa_instance_state']
        # Delete the "sa_instance_state" element because it can not be passed into json
        return jsonify(cafe=random_cafe)
        # to turn our random_cafe SQLAlchemy Object into a JSON.
        # This process is called serialization.
        # we use jsonify()


## HTTP GET - Read Record
# GET THE WHOLE LIST
@app.route('/all')
def read_record():
    cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in cafes:
        cafe = cafe.__dict__
        del cafe['_sa_instance_state']
        cafe_list.append(cafe)

    return jsonify(cafe=cafe_list)


# GET A CAFE FROM ITS LOCATION
@app.route('/search')
def search_cafe():
    loc = request.args.get("loc")
    cafes = db.session.query(Cafe).filter(Cafe.location == loc).all()
    cafe_list = []
    if cafes:
        for cafe in cafes:
            cafe = cafe.__dict__
            del cafe['_sa_instance_state']
            cafe_list.append(cafe)
        return jsonify(cafe=cafe_list)

    return jsonify(error={'Not Found': 'Sorry, no cafe at this location'})


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:id>', methods=['PATCH', 'GET'])
def update_price(id):
    cafe = db.session.query(Cafe).get(id)
    price = request.args.get("new_price")
    if cafe:
        cafe.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})

    return jsonify(error={'Not Found': 'Sorry, no cafe at this id'})


## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:id>')
def delete(id):
    cafe = db.session.query(Cafe).get(id)
    api_entered = request.args.get('api-key')
    if api_entered == API_KEY:
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "the cafe has been removed."})

        return jsonify(error={'Not Found': 'Sorry, no cafe at this id'})

    return jsonify(error={'Not authorised': 'Sorry, you cannot access the database'})


if __name__ == '__main__':
    app.run(debug=True)
