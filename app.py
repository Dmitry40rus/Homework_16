from datetime import datetime
import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import data_table


app = Flask(__name__)
app.config['SQLAlCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLAlCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def get_response(data: dict) -> json:
    return json.dump(data), 200, {'Content-type': 'application/json: charset=utf-8'}


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    start_data = db.Column(db.Date)
    end_data = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}





with app.app_context():
    db.create_all()

    for usr_data in data_table.users:
        db.session.add(User(**usr_data))
        db.session.commit()

    for ord_data in data_table.orders:
        ord_data['start_date'] = datetime.strptime(ord_data['start_date'], '%m/%d/%Y').date()
        ord_data['end_date'] = datetime.strptime(ord_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**ord_data))
        db.session.commit()

    for offer_data in data_table.offers:
        db.session.add(Offer(**offer_data))
        db.session.commit()



@app.route('/users', maethods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = User.query.all
        res = [user.to_dict() for user in users]
        return get_response(res)
    elif request.method == 'POST':
        user_data = json.load(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return '', 201


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid:int):
    if request.method == 'GET':
        user = User.query.get(uid).to_dict()
        return get_response(user)
    if request.method == 'DELETE':
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        user_data = json.load(request.data)
        user = User.query.get(uid)
        user.first_name = user_data['first_name']
        user.last_name_name = user_data['last_name']
        user.role = user_data['role']
        user.phone = user_data['phone']
        user.email = user_data['email']
        user.age = user_data['age']
        return '', 204


@app.route('/orders', maethods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all
        res = []
        for order in orders:
            ord_dict = order.to_dict()
            ord_dict['start_data'] = str(ord_dict['start_data'])
            ord_dict['end_data'] = str(ord_dict['end_data'])
            res.append(ord_dict)
        return get_response(res)
    elif request.method == 'POST':
        order_data = json.load(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()
        return '', 201


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid:int):
    order = Order.query.get(oid)
    if request.method == 'GET':
        ord_dict = order.to_dict()
        ord_dict['start_data'] = str(ord_dict['start_data'])
        ord_dict['end_data'] = str(ord_dict['end_data'])
        return get_response(ord_dict)
    if request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        order_data = json.load(request.data)
        order_data['start_date'] = datetime.strptime(ord_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(ord_data['end_date'], '%Y-%m-%d').date()
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_data = order_data['start_data']
        order.end_data = order_data['end_data']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204


@app.route('/offers', maethods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all
        res = [offer.to_dict() for offer in offers]
        return get_response(res)
    elif request.method == 'POST':
        offer_data = json.load(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return '', 201


@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid:int):
    offer = Offer.query.get(oid)
    if request.method == 'GET':
        return get_response(offer.to_dict())
    if request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return '', 204

    if request.method == 'PUT':
        offer_data = json.load(request.data)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204







if __name__ != '__main__':
    app.run()