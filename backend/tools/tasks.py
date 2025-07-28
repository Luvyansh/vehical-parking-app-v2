from tools.workers import celery
from applications.models import *
from tools.mail_bot import send_email
from flask import render_template
from datetime import timedelta
from celery.schedules import crontab
import io
import csv

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10*60, send_daily_remainders.s(), name='send_daily_remainders')
    #sender.add_periodic_task(crontab(hour=10, minute=30), send_daily_remainders.s(), name='send_daily_remainders_at_10:30')
    sender.add_periodic_task(10*60, send_monthly_reports.s(), name='send_monthly_reports')

@celery.task()
def add(x, y):
    return x + y

@celery.task()
def send_reservation_email(reservation_id):
    reservation = ReservedParking.query.get_or_404(reservation_id)
    user = User.query.get_or_404(reservation.user_id)
    spot = ParkingSpot.query.get_or_404(reservation.spot_id)
    lot = ParkingLot.query.get_or_404(spot.lot_id)
    email = user.email
    #Send email to user
    to = email
    subject = f'Reservation for Spot {reservation.spot_id} has been confirmed'
    html = render_template(
        'reservation_email.html',
        user_name=user.name,
        user_username=user.username,
        reservation_spot_id=reservation.spot_id,
        lot_prime_location_name=lot.prime_location_name,
        spot_id=spot.id,
        reservation_park_time=reservation.park_time,
        lot_price=lot.price,
        current_year=datetime.now().year
    )
    send_email(to=to, subject=subject, html=html)
    return "Email sent successfully"

@celery.task()
def send_release_email(reservation_id):
    reservation = ReservedParking.query.get_or_404(reservation_id)
    user = User.query.get_or_404(reservation.user_id)
    spot = ParkingSpot.query.get_or_404(reservation.spot_id)
    lot = ParkingLot.query.get_or_404(spot.lot_id)

    html = render_template(
        'release_email.html', # Assuming you save this as release_email_template.html
        user_name=user.name,
        user_username=user.username,
        reservation_spot_id=reservation.spot_id,
        lot_prime_location_name=lot.prime_location_name,
        spot_id=spot.id,
        reservation_park_time=reservation.park_time,
        reservation_exit_time=reservation.exit_time,
        reservation_total_cost=reservation.total_cost,
        current_year=datetime.now().year
    )

    email = user.email
    to = email
    subject = f'Reservation for Spot {reservation.spot_id} has been released'

    send_email(to=to, subject=subject, html=html)
    return "Email sent successfully"

@celery.task()
def send_daily_remainders():
    """
    Send daily remainders to all the users who haven't logged in since the last 24 hours
    """
    day_ago = datetime.now() - timedelta(hours=24)
    # Get all the users except admin who haven't logged in since the last 24 hours
    users = User.query.filter_by(admin=False).filter(User.last_login < day_ago).all()
    for user in users:
        to = user.email
        subject = "Daily Reminder"
        html = render_template('daily_reminder.html', user_name=user.name, current_year=datetime.now().year)
        send_email(to=to, subject=subject, html=html)
    return "Email sent successfully"

@celery.task()
def send_monthly_reports():
    today = datetime.now()
    # Calculate the start date for the last 30 days
    start_date = today - timedelta(days=30)
    end_date = today # End date is today

    # Fetch all reservations within the last 30 days
    # Ensure ReservedParking.park_time is a proper datetime column
    past_month_reservations = ReservedParking.query.filter(
        ReservedParking.park_time.between(start_date, end_date)
    ).all()

    # Group reservations by user
    user_reservations = {}
    for reservation in past_month_reservations:
        user_id = reservation.user_id
        if user_id not in user_reservations:
            user_reservations[user_id] = []
        user_reservations[user_id].append(reservation)

    # Iterate through each user and send their report
    for user_id, reservations in user_reservations.items():
        user = User.query.get(user_id)
        if user: # Ensure user exists before sending email
            to = user.email
            subject = f"Your Monthly Parking Report - {user.name} - ParkingPal"

            # 1. Generate HTML content for the email body
            # Assuming 'monthly_report.html' is a Jinja2 template that displays reservation details
            html_body = render_template(
                'monthly_report.html',
                user_name=user.name,
                reservations=reservations, # Pass reservations to the HTML template as well
                current_year=datetime.now().year
            )

            # 2. Generate CSV report data
            csv_data_bytes = generate_monthly_csv_report(reservations)

            # 3. Prepare the attachment list
            attachments = [
                {
                    'filename': f'monthly_report_{user.username}_{today.strftime("%Y-%m")}.csv',
                    'content_type': 'text/csv',
                    'data': csv_data_bytes
                }
            ]

            # 4. Send the email with HTML body and CSV attachment
            send_email(to=to, subject=subject, html=html_body, attachments=attachments)
        else:
            print(f"Warning: User with ID {user_id} not found for sending monthly report.")

    return "Monthly reports sent successfully"

def generate_monthly_csv_report(reservations):
    output = io.StringIO()
    writer = csv.writer(output)

    # Define CSV headers
    writer.writerow([
        'Reservation ID', 'Spot ID', 'Parking Lot Name', 'Park Time',
        'Exit Time', 'Total Cost'
    ])

    # Write data for each reservation
    for res in reservations:
        # Fetch related spot and lot details for the report
        spot = ParkingSpot.query.get(res.spot_id)
        lot_name = ParkingLot.query.get(spot.lot_id).prime_location_name if spot and spot.lot_id else 'N/A'

        writer.writerow([
            res.id,
            res.spot_id,
            lot_name,
            res.park_time.strftime('%Y-%m-%d %H:%M:%S') if res.park_time else 'N/A',
            res.exit_time.strftime('%Y-%m-%d %H:%M:%S') if res.exit_time else 'N/A',
            f"{res.total_cost:.2f}" if res.total_cost is not None else 'N/A'
        ])

    # Get the string value and encode it to bytes
    csv_content = output.getvalue()
    return csv_content.encode('utf-8')