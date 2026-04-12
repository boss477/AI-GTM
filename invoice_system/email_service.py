import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(to_email: str, subject: str, body: str, attachment: str = None):
    """Send an email with an optional PDF attachment."""
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = to_email

    msg.attach(MIMEText(body, "plain"))

    if attachment and os.path.exists(attachment):
        with open(attachment, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment)}"'
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
