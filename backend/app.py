from applications import app, db, User
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from applications.models import *
from faker import Faker # type: ignore
import random
from datetime import datetime, timedelta

def create_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(admin=True).first():
            user = User(
                name="Admin",
                username="admin",
                email="admin@park.com",
                password="22f1000812",
                admin=True
            )
            db.session.add(user)
            db.session.commit()

create_admin()

#Generating Random Data to store in the Database
fake = Faker()

def seed_dummy_data(num_users=5, num_locations=5, lots_per_location=2, spots_per_lot=10):
    for _ in range(num_users):
        name = fake.name()
        username = fake.user_name()
        email = fake.unique.email()
        user = User(name=name, username=username, email=email, password="1234")
        db.session.add(user)

    db.session.commit()

    # Add Dummy Locations, Lots, Spots
    all_spots = []
    for _ in range(num_locations):
        location_name = fake.street_name()
        city = fake.city()
        lat = fake.latitude()
        lon = fake.longitude()

        location = Location(name=location_name, city=city, latitude=lat, longitude=lon)
        db.session.add(location)
        db.session.commit()

        for _ in range(lots_per_location):
            prime_location_name = fake.company()
            price = round(random.uniform(10, 100), 2)
            address = fake.address()
            pin_code = fake.postcode()[:6]
            number_of_spots = spots_per_lot

            lot = ParkingLot(prime_location_name, price, address, pin_code, number_of_spots)
            lot.location_id = location.id
            db.session.add(lot)
            db.session.commit()

            for _ in range(spots_per_lot):
                spot = ParkingSpot(lot_id=lot.id, is_available=True)
                db.session.add(spot)
                db.session.commit()
                all_spots.append(spot)

    users = User.query.filter_by(admin=False).all()
    for _ in range(min(10, len(all_spots))):
        user = random.choice(users)
        spot = random.choice(all_spots)

        park_time = datetime.now() - timedelta(hours=random.randint(1, 24))
        exit_time = park_time + timedelta(hours=random.randint(1, 5))
        total_cost = round(random.uniform(10, 100), 2)

        reservation = ReservedParking(user_id=user.id, spot_id=spot.id, park_time=park_time, exit_time=exit_time, total_cost=total_cost)
        db.session.add(reservation)

    db.session.commit()
    print("✅ Dummy data seeded successfully.")

# Run dummy seeder only if there are 1 or fewer users (i.e. just the admin)
with app.app_context():
    user_count = User.query.count()
    if user_count <= 1:
        print("🔄 Seeding dummy data...")
        seed_dummy_data()
    else:
        pass

if __name__ == "__main__":
    #print(app.url_map)
    app.run(debug=True)

from applications import celery