from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Café TABLE Configuration
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

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    cafes = Cafe.query.all()
    random_cafe = random.choice(cafes)
    cafe_dict = random_cafe.to_dict()
    return jsonify(cafe=cafe_dict)


@app.route("/all")
def all_cafes():
    cafes = Cafe.query.all()
    data = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=data)


@app.route("/search")
def search_by_location():
    location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=location).all()
    data = [cafe.to_dict() for cafe in cafes]
    if len(data) > 0:
        return jsonify(cafes=data)
    else:
        error = {
            "Not Found": f"Sorry, we do not have a cafe at {location}"
        }
        return jsonify(error=error)


@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form["name"],
        map_url=request.form["map_url"],
        img_url=request.form["img_url"],
        location=request.form["location"],
        has_sockets=bool(int(request.form["has_sockets"])),
        has_toilet=bool(int(request.form["has_toilet"])),
        has_wifi=bool(int(request.form["has_wifi"])),
        can_take_calls=bool(int(request.form["can_take_calls"])),
        seats=request.form["seats"],
        coffee_price=request.form["coffee_price"]
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={
        "success": "Successfully added the new cafe"
    })


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        new_price = request.args.get("new_price")
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price"), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found"}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Cafe was successfully deleted")
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found"}), 404
    else:
        return jsonify(error="Sorry, that\'s not allowed. Make sure you have the correct api key"), 403


if __name__ == '__main__':
    app.run(debug=True)
