from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, unset_jwt_cookies
from applications.models import *
from applications import app, db, bcrypt
from applications.auth_utils import admin_required, user_required
from tools import tasks

@app.route("/", methods=["GET"])
def index():
    tasks.add.delay(1, 2)
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
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

@app.route("/get_locations", methods=["GET"])
@jwt_required()
def get_locations():
    locations = Location.query.all()
    return jsonify({"locations": [loc.to_dict() for loc in locations]}), 200

##################################################################################
############################CRUD on Admin Dashboard###############################
##################################################################################

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

@app.route("/update_parking_lot/<int:lot_id>", methods=["PUT"])
@admin_required
def update_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if not lot:
        return jsonify({"message": "Parking lot not found"}), 404
    data = request.get_json()
    name = data.get("prime_location_name")
    price = data.get("price")
    address = data.get("address")
    pin_code = data.get("pin_code")
    number_of_spots = data.get("number_of_spots")
    lot.prime_location_name = name
    lot.price = price
    lot.address = address
    lot.pin_code = pin_code
    lot.number_of_spots = number_of_spots
    db.session.commit()
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

@app.route('/search', methods=['GET'])
@admin_required
def admin_search():
    query = request.args.get('q', '').lower()
    users, lots, reservations = [], [], []
    
    #If query = "all", return all users, lots, and reservations
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
                "Park Time": res.park_time,
                "Exit Time": res.exit_time
            })
        return jsonify({"users": users, "lots": lots, "reservations": reservations}), 200

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
                "Park Time": res.park_time.strftime("%Y-%m-%d %H:%M"),
                "Exit Time": res.exit_time.strftime("%Y-%m-%d %H:%M"),
                "Cost": res.total_cost
            })

    return jsonify({
        "users": users,
        "lots": lots,
        "reservations": reservations
    })

##################################################################################
############################CRUD on User Dashboard################################
##################################################################################

@app.route("/reserve_spot", methods=["POST"])
@user_required
def reserve_spot():
    user_id = get_jwt_identity()
    data = request.get_json()

    spot_id = data.get("spot_id")
    park_time_str = data.get("park_time")

    # Validate required fields
    if not all([spot_id, park_time_str]):
        return jsonify({"message": "Missing required fields"}), 400

    # Validate spot
    spot = ParkingSpot.query.get_or_404(spot_id)
    if not spot.is_available:
        return jsonify({"message": "Spot already reserved"}), 400

    try:
        park_time = datetime.fromisoformat(park_time_str)
    except Exception:
        return jsonify({"message": "Invalid data format"}), 400

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

@app.route("/release_parking/<int:reservation_id>", methods=["PUT"])
@user_required
def release_parking(reservation_id):
    # Validate if current user = user who reserved the spot
    user_id = int(get_jwt_identity()) #get_jwt_identity returns a string
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
    return jsonify({"message": "Parking released successfully"}), 200

@app.route("/user_search/<string:query>", methods=["GET"])
@user_required
def user_search(query: str):
    lots = []
    reservations = []
    for lot in ParkingLot.query.all():
        if query in lot.prime_location_name.lower() or query in lot.address.lower() or query in str(lot.pin_code):
            lots.append({
                "ID": lot.id,
                "Location": lot.prime_location_name,
                "Address": lot.address,
                "Pin": lot.pin_code,
                "Price": lot.price
            })

    for res in ReservedParking.query.filter_by(user_id=get_jwt_identity()).all():
        if query in str(res.user_id) or query in str(res.spot_id) or query in str(res.id):
            reservations.append({
                "ID": res.id,
                "User ID": res.user_id,
                "Spot ID": res.spot_id,
                "Park Time": res.park_time.strftime("%Y-%m-%d %H:%M"),
                "Exit Time": res.exit_time.strftime("%Y-%m-%d %H:%M"),
                "Cost": res.total_cost
            })

    return jsonify({
        "lots": lots,
        "reservations": reservations
    })

@app.route("/get_user_reservations/<string:user_name>", methods=["GET"])
@user_required
def get_user_reservations(user_name):
    user_id = User.query.filter_by(username=user_name).first().id
    reservations = ReservedParking.query.filter_by(user_id=user_id).all()
    return jsonify({"reservations": [res.to_dict() for res in reservations]}), 200