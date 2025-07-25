from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    last_login = db.Column(db.DateTime, default=datetime.now)
    reservations = db.relationship('ReservedParking', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, username, email, password, admin=False):
        self.name = name
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.admin = admin

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "admin": self.admin,
            "last_login": self.last_login
        }

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prime_location_name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id', ondelete='CASCADE'), nullable=False)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete-orphan")

    def __init__(self, prime_location_name, price, address, pin_code, number_of_spots):
        self.prime_location_name = prime_location_name
        self.price = price
        self.address = address
        self.pin_code = pin_code
        self.number_of_spots = number_of_spots
    
    def to_dict(self):
        return {
            "id": self.id,
            "prime_location_name": self.prime_location_name,
            "price": self.price,
            "address": self.address,
            "pin_code": self.pin_code,
            "number_of_spots": self.number_of_spots,
            "location_id": self.location_id
        }

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id', ondelete='CASCADE'), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    reservation = db.relationship('ReservedParking', backref='spot', lazy=True, cascade="all, delete-orphan")

    def __init__(self, lot_id, is_available=True):
        self.lot_id = lot_id
        self.is_available = is_available
    
    def to_dict(self):
        return {
            "id": self.id,
            "lot_id": self.lot_id,
            "is_available": self.is_available
        }

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    lots = db.relationship('ParkingLot', backref='location', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, city, latitude, longitude):
        self.name = name
        self.city = city
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "lots": [lot.to_dict() for lot in self.lots]
        }

class ReservedParking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id', ondelete='CASCADE'), nullable=False)
    park_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

    def __init__(self, user_id, spot_id, park_time, exit_time, total_cost):
        self.user_id = user_id
        self.spot_id = spot_id
        self.park_time = park_time
        self.exit_time = exit_time
        self.total_cost = total_cost
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "spot_id": self.spot_id,
            "park_time": self.park_time,
            "exit_time": self.exit_time,
            "total_cost": self.total_cost
        }


from sqlalchemy.orm import Session
from sqlalchemy import event

@event.listens_for(User, 'before_delete')
def free_reserved_spots(mapper, connection, target):
    session = Session(bind=connection)
    reservations = session.query(ReservedParking).filter_by(user_id=target.id).all()
    for res in reservations:
        spot = session.query(ParkingSpot).get(res.spot_id)
        if spot:
            spot.is_available = True
            session.add(spot)
    session.commit()

@event.listens_for(ReservedParking, 'before_insert')
def update_spot_availability(mapper, connection, target):
    session = Session(bind=connection)

    spot = session.query(ParkingSpot).get(target.spot_id)
    if not spot:
        return

    # Update availability based on exit_time
    if target.exit_time < datetime.now():
        spot.is_available = True
    else:
        spot.is_available = False

    session.add(spot)
    session.commit()