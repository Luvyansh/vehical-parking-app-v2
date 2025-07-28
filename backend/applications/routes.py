from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, unset_jwt_cookies
from applications.models import *
from applications import app, db, bcrypt
from applications.auth_utils import admin_required, user_required
from tools import tasks
from flask_caching import Cache

cache = Cache(app)

#@cache.cached(timeout=10)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# ✅ User registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400
    
    user = User(name=name, username=username, email=email, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error registering user"}), 500

# ✅ User login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        # ✅ Update last_login time
        user.last_login = datetime.now()
        db.session.commit()

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "username": user.username,
                "email": user.email,
                "admin": user.admin
            }
        )
        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200

    return jsonify({"message": "Invalid username or password"}), 401

@app.route("/get_user_info", methods=["GET"])
@jwt_required()
def get_user_info():
    claims = get_jwt()
    return jsonify({
        "user": {
            "username": claims["username"],
            "email": claims["email"],
            "admin": claims["admin"]
        }
    }), 200

@app.route("/admin_dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    return jsonify({"msg": "Welcome admin!"})

@app.route("/user_dashboard", methods=["GET"])
@user_required
def user_dashboard():
    return jsonify({"msg": "Welcome user!"})

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

@cache.cached(timeout=60*60)
@app.route("/get_locations", methods=["GET"])
def get_locations():
    locations = Location.query.all()
    return jsonify({"locations": [loc.to_dict() for loc in locations]}), 200

@cache.cached(timeout=60*60)
@app.route("/get_lots", methods=["GET"])
@jwt_required()
def get_lots():
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()
    return jsonify({
        "lots": [lot.to_dict() for lot in lots],
        "spots": [spot.to_dict() for spot in spots]
    }), 200

##################################################################################
############################CRUD on Admin Dashboard###############################
##################################################################################

@cache.cached(timeout=60*60)
@app.route("/parking_lots", methods=["GET"])
@admin_required
def parking_lots():
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()
    reservedSpots = ReservedParking.query.all()
    return jsonify({
        "lots": [lot.to_dict() for lot in lots],
        "spots": [spot.to_dict() for spot in spots],
        "reservedSpots": [reservedSpot.to_dict() for reservedSpot in reservedSpots]
    }), 200

@app.route("/add_location", methods=["POST"])
@admin_required
def add_location():
    data = request.get_json()
    name = data.get("name")
    city = data.get("city")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    loc = Location(name, city, latitude, longitude)
    if Location.query.filter_by(name=name).first():
        return jsonify({"message": "Location already exists"}), 400
    db.session.add(loc)
    db.session.commit()
    return jsonify({"message": "Location added successfully"}), 201

@app.route("/delete_location/<int:location_id>", methods=["DELETE"])
@admin_required
def delete_location(location_id):
    loc = Location.query.get(location_id)
    if not loc:
        return jsonify({"message": "Location not found"}), 404
    db.session.delete(loc)
    db.session.commit()
    return jsonify({"message": "Location deleted successfully"}), 200

@app.route("/add_parking_lot", methods=["POST"])
@admin_required
def add_parking_lot():
    data = request.get_json()
    name = data.get("prime_location_name")
    price = data.get("price")
    address = data.get("address")
    pin_code = data.get("pin_code")
    number_of_spots = data.get("number_of_spots")
    location_id = data.get("location_id")
    if not Location.query.get(location_id):
        return jsonify({"message": "Invalid location ID"}), 400
    lot = ParkingLot(name, price, address, pin_code, number_of_spots)
    lot.location_id = location_id
    #Check if lot already exists
    if ParkingLot.query.filter_by(prime_location_name=name).first():
        return jsonify({"message": "Parking lot already exists"}), 400
    else:
        db.session.add(lot)
        db.session.commit()
        
        #Adding parking spots
        spots = [ParkingSpot(lot_id=lot.id) for _ in range(number_of_spots)]
        db.session.add_all(spots)
        db.session.commit()
        return jsonify({"message": "Parking lot added successfully"}), 201

@app.route("/update_parking_lot/<int:lot_id>", methods=["POST"])
@admin_required
def update_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    previous_number_of_spots = lot.number_of_spots

    data = request.get_json()

    if not all(k in data for k in ["prime_location_name", "price", "address", "pin_code", "number_of_spots"]):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        new_number_of_spots = int(data["number_of_spots"])
        if new_number_of_spots < 0:
            return jsonify({"message": "Number of spots cannot be negative"}), 400
        new_price = float(data["price"])
        if new_price < 0:
            return jsonify({"message": "Price cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "Invalid data type for price or number_of_spots"}), 400

    lot.prime_location_name = data["prime_location_name"]
    lot.price = new_price
    lot.address = data["address"]
    lot.pin_code = data["pin_code"]
    lot.number_of_spots = new_number_of_spots
    
    db.session.commit()


    if new_number_of_spots > previous_number_of_spots:
        spots_to_add = [ParkingSpot(lot_id=lot.id)
                        for _ in range(new_number_of_spots - previous_number_of_spots)]
        db.session.add_all(spots_to_add)
        db.session.commit()
        return jsonify({"message": "Parking lot and new spots added successfully"}), 200

    elif new_number_of_spots < previous_number_of_spots:
        num_to_delete = previous_number_of_spots - new_number_of_spots

        all_spots_in_lot = ParkingSpot.query.filter_by(lot_id=lot.id).order_by(ParkingSpot.id.desc()).all()
        
        current_utc_time = datetime.now()

        deletable_spots = []
        for spot in all_spots_in_lot:
            if not spot.is_available:
                continue

            active_reservation_exists = ReservedParking.query.filter(
                ReservedParking.spot_id == spot.id,
                (ReservedParking.exit_time == None) | (ReservedParking.exit_time > current_utc_time)
            ).first()

            if not active_reservation_exists:
                deletable_spots.append(spot)

        if num_to_delete > len(deletable_spots):
            db.session.rollback() 
            return jsonify({
                "message": (f"Cannot reduce spots to {new_number_of_spots}. "
                            f"There are {len(all_spots_in_lot) - len(deletable_spots)} spots with active reservations "
                            "that cannot be deleted.")
            }), 400
        
        spots_to_remove = deletable_spots[:num_to_delete]

        for spot in spots_to_remove:
            db.session.delete(spot)
        
        db.session.commit()
        return jsonify({"message": "Parking lot and spots reduced successfully"}), 200

    return jsonify({"message": "Parking lot updated successfully"}), 200

@app.route("/delete_parking_lot/<int:lot_id>", methods=["DELETE"])
@admin_required
def delete_parking_lot(lot_id):
    #Check if any spot inside the parking lot is reserved
    lot = ParkingLot.query.get_or_404(lot_id)
    for spot in lot.spots:
        if ReservedParking.query.filter_by(spot_id=spot.id).first():
            return jsonify({"message": "Cannot delete lot with reserved spots"}), 400
    
    if not lot:
        return jsonify({"message": "Parking lot not found"}), 404
    db.session.delete(lot)
    db.session.commit()
    return jsonify({"message": "Parking lot deleted successfully"}), 200

@cache.cached(timeout=60*60)
@app.route("/get_users", methods=["GET"])
@admin_required
def get_users():
    users = User.query.filter_by(admin=False).all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200

@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@cache.cached(timeout=60*60)
@app.route('/search', methods=['GET'])
@admin_required
def admin_search():
    query = request.args.get('q', '').lower()
    users, lots, reservations = [], [], []

    # Helper function to format cost (DRY principle)
    def format_cost(cost_value):
        if isinstance(cost_value, (int, float)):
            return f"{float(cost_value):.2f}" # Pythonic way to format float to 2 decimal places
        return cost_value # Return as is if not a number (e.g., None, string)

    # If query = "all", return all users, lots, and reservations
    if query == "all":
        for user in User.query.filter_by(admin=False).all():
            users.append({
                "ID": user.id,
                "Name": user.name,
                "Username": user.username,
                "Email": user.email
            })
        for lot in ParkingLot.query.all():
            lots.append({
                "ID": lot.id,
                "Location": lot.prime_location_name,
                "Address": lot.address,
                "Pin": lot.pin_code,
                "Price": lot.price
            })
        for res in ReservedParking.query.all():
            reservations.append({
                "ID": res.id,
                "User ID": res.user_id,
                "Spot ID": res.spot_id,
                "Park Time": res.park_time.strftime("%Y-%m-%d %H:%M") if res.park_time else "N/A",
                "Exit Time": res.exit_time.strftime("%Y-%m-%d %H:%M") if res.exit_time else "N/A",
                "Total Cost": format_cost(res.total_cost) # ⭐ FIXED HERE ⭐
            })
        return jsonify({"users": users, "lots": lots, "reservations": reservations}), 200

    # Search for specific queries
    for user in User.query.filter_by(admin=False).all():
        if query in user.name.lower() or query in user.username.lower() or query in user.email.lower():
            users.append({
                "ID": user.id,
                "Name": user.name,
                "Username": user.username,
                "Email": user.email
            })

    for lot in ParkingLot.query.all():
        if query in lot.prime_location_name.lower() or query in lot.address.lower() or query in str(lot.pin_code):
            lots.append({
                "ID": lot.id,
                "Location": lot.prime_location_name,
                "Address": lot.address,
                "Pin": lot.pin_code,
                "Price": lot.price
            })

    for res in ReservedParking.query.all():
        if query in str(res.user_id) or query in str(res.spot_id) or query in str(res.id):
            reservations.append({
                "ID": res.id,
                "User ID": res.user_id,
                "Spot ID": res.spot_id,
                "Park Time": res.park_time.strftime("%Y-%m-%d %H:%M") if res.park_time else "N/A",
                "Exit Time": res.exit_time.strftime("%Y-%m-%d %H:%M") if res.exit_time else "N/A",
                "Total Cost": format_cost(res.total_cost) # ⭐ FIXED HERE ⭐
            })

    return jsonify({
        "users": users,
        "lots": lots,
        "reservations": reservations
    })

@app.route("/admin_summary", methods=["GET"])
@admin_required
def admin_summary():
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()
    reservations = ReservedParking.query.all()
    users = User.query.filter_by(admin=False).all()
    return jsonify({
        "lots": [lot.to_dict() for lot in lots],
        "spots": [spot.to_dict() for spot in spots],
        "reservations": [res.to_dict() for res in reservations],
        "users": [user.to_dict() for user in users]
    })

##################################################################################
############################CRUD on User Dashboard################################
##################################################################################

@cache.cached(timeout=60*60)
@app.route("/get_spots_in_lot/<int:lot_id>", methods=["GET"])
@user_required
def get_spots_in_lot(lot_id):
    try:
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify({
            "spots": [spot.to_dict() for spot in spots]
        }), 200
    except Exception as e:
        return jsonify({"error": "Could not retrieve spots", "details": str(e)}), 500

from datetime import datetime
# ... other imports

@app.route("/reserve_spot/<int:spot_id>", methods=["POST"])
@user_required
def reserve_spot(spot_id):
    user_id = get_jwt_identity()

    # Get the current time directly as a datetime object
    park_time = datetime.now()

    # Validate spot
    spot = ParkingSpot.query.get_or_404(spot_id)
    if not spot.is_available:
        return jsonify({"message": "Spot already reserved"}), 400

    # Reserve and update
    reserved_parking = ReservedParking(user_id, spot_id, park_time, None, None)
    spot.is_available = False

    db.session.add(reserved_parking)
    db.session.commit()

    # Store the reservation ID in reservation_id
    reservation_id = reserved_parking.id
    
    tasks.send_reservation_email.delay(reservation_id)

    return jsonify({
        "message": "Spot reserved successfully",
        "reservation": reserved_parking.to_dict()
    }), 200

@app.route("/release_parking/<int:reservation_id>", methods=["POST"])
@user_required
def release_parking(reservation_id):
    if request.method == "OPTIONS":
        return jsonify({"message": "Success"}), 200
    
    user_id = int(get_jwt_identity())
    if user_id is None:
        return jsonify({"message": "User not found"}), 404
    
    reservation = ReservedParking.query.get_or_404(reservation_id)

    if reservation.user_id != user_id:
        return jsonify({"message": "You are not authorized to release this spot. User who booked the spot is: " + str(reservation.user_id) + " and you are: " + str(user_id)}), 403
    
    exit_time = datetime.now()
    reservation.exit_time = exit_time
    spot = ParkingSpot.query.get_or_404(reservation.spot_id)
    lot = ParkingLot.query.get_or_404(spot.lot_id)
    price_per_hour = lot.price * (exit_time - reservation.park_time).total_seconds() / 3600
    total_cost = (exit_time - reservation.park_time).total_seconds() / 3600 * price_per_hour
    reservation.total_cost = total_cost
    spot.is_available = True
    db.session.add(reservation)
    db.session.add(spot)
    db.session.commit()
    
    reservation_id = reservation.id
    tasks.send_release_email.delay(reservation_id)

    return jsonify({"message": "Parking released successfully"}), 200

@cache.cached(timeout=60*60)
@app.route("/user_search", methods=["GET"])
@user_required
def user_search():
    query = request.args.get("query", "").lower()
    lots = []
    reservations = []

    for lot in ParkingLot.query.all():
        if (
            query in lot.prime_location_name.lower()
            or query in lot.address.lower()
            or query in str(lot.pin_code)
            or query in str(lot.price)
        ):
            lots.append({
                "ID": lot.id,
                "Location": lot.prime_location_name,
                "Address": lot.address,
                "Pin": lot.pin_code,
                "Price": lot.price
            })

    for res in ReservedParking.query.filter_by(user_id=get_jwt_identity()).all():
        if (
            query in str(res.id)
            or query in str(res.user_id)
            or query in str(res.spot_id)
            or (res.park_time and query in res.park_time.strftime("%Y-%m-%d %H:%M").lower())
            or (res.exit_time and query in res.exit_time.strftime("%Y-%m-%d %H:%M").lower())
            or (res.total_cost and query in str(res.total_cost))
        ):
            reservations.append({
                "ID": res.id,
                "User ID": res.user_id,
                "Spot ID": res.spot_id,
                "Park Time": res.park_time.strftime("%Y-%m-%d %H:%M"),
                "Exit Time": res.exit_time.strftime("%Y-%m-%d %H:%M") if res.exit_time else "N/A",
                "Total Cost": res.total_cost
            })

    return jsonify({
        "lots": lots,
        "reservations": reservations
    })

def no_of_available_spots(lot_id):
    return ParkingSpot.query.filter_by(lot_id=lot_id, is_available=True).count()

@cache.cached(timeout=60*60)
@app.route("/get_user_reservations/<string:user_name>", methods=["GET"])
@user_required
def get_user_reservations(user_name):
    user_id = User.query.filter_by(username=user_name).first().id
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()
    locations = Location.query.all()
    reservations = ReservedParking.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "lots": [lot.to_dict() for lot in lots],
        "spots": [spot.to_dict() for spot in spots],
        "locations": [loc.to_dict() for loc in locations],
        "reservations": [res.to_dict() for res in reservations]
        }), 200

@app.route("/available_spots/<int:lot_id>", methods=["GET"])
@user_required
def available_spots(lot_id):
    count = ParkingSpot.query.filter_by(lot_id=lot_id, is_available=True).count()
    return jsonify({"available_spots": count}), 200

@app.route("/user_summary", methods=["GET"])
@user_required
def user_summary():
    user_id = int(get_jwt_identity())
    lots = ParkingLot.query.all()
    spots = ParkingSpot.query.all()
    reservations = ReservedParking.query.filter_by(user_id=user_id).all()
    return jsonify({
        "lots": [lot.to_dict() for lot in lots],
        "spots": [spot.to_dict() for spot in spots],
        "reservations": [res.to_dict() for res in reservations]
        }), 200

@cache.cached(timeout=60*60)
@app.route("/get_usernames", methods=["GET"])
@user_required
def get_usernames():
    users = User.query.filter_by(admin=False).all()
    return jsonify({"usernames": [user.username for user in users]}), 200

@cache.cached(timeout=60*60)
@app.route("/user_profile", methods=["GET"])
@user_required
def user_profile():
    user = User.query.get(get_jwt_identity())
    #only return name, username, email
    return jsonify({
        "name": user.name,
        "username": user.username,
        "email": user.email
    }), 200

@app.route("/update_user_info", methods=["POST"])
@user_required
def update_user_info():
    data = request.get_json()
    user = User.query.get(get_jwt_identity())
    user.name = data.get("name")
    user.username = data.get("username")
    user.email = data.get("email")
    db.session.commit()
    return jsonify({"message": "User information updated successfully"}), 200

##################################################################################
###############################Cache Management###################################
##################################################################################

@app.route("/clear_cache", methods=["POST"])
@admin_required
def clear_cache():
    cache.clear()
    return jsonify({"message": "Cache cleared successfully"}), 200