import smtplib
from email.mime.text import MIMEText
import os
import json

from dotenv import load_dotenv

load_dotenv()

#the data will be stored in separated file to secure user data 
SENDER = os.getenv("SENDER")
PASSWORD = os.getenv("PASSWORD")
RECIPIENTS = os.getenv("RECIPIENTS").split(",")

#Definition from SMTP and secret data
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = ', '.join(RECIPIENTS)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(SENDER, PASSWORD)
    smtp_server.sendmail(SENDER, RECIPIENTS, msg.as_string())
    smtp_server.quit()

