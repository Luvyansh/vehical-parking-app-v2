from flask_mail import Message, Mail
from flask import current_app as app

mail = Mail()

def init_app(app):
    mail.init_app(app)

def send_email(to, subject, body=None, html=None, attachments=None):
    sender = 'noreply@parkpal.com'
    
    msg = Message(subject, sender=sender, recipients=[to])
    if body:
        msg.body = body
    if html:
        msg.html = html
    # Add attachments if provided
    if attachments:
        for attachment in attachments:
            if all(key in attachment for key in ['filename', 'content_type', 'data']):
                msg.attach(
                    filename=attachment['filename'],
                    content_type=attachment['content_type'],
                    data=attachment['data']
                )
            else:
                # Print a warning for malformed attachments (consider more robust logging in production)
                print(f"Warning: Skipping malformed attachment: {attachment}. Missing 'filename', 'content_type', or 'data'.")
    # Ensure this is called within a Flask application context
    with app.app_context():
        mail.send(msg)