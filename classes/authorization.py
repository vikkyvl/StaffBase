import smtplib
import random
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Authorization:
    def __init__(self, sender_email = "staff-base@ukr.net", sender_password = "6tOvCUvuZh5MrCsg"):
        self.sender_email = sender_email
        self.sender_password = sender_password

    @staticmethod
    def generate_verification_code(length=6):
        return ''.join(random.choices('0123456789', k=length))

    def send_email(self, receiver_email, verification_code):
        subject = "Password change"
        body = f"Your verification code: {verification_code}"

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.ukr.net", 465, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, receiver_email, message.as_string())
            print("The letter has been successfully sent!")
        except Exception as e:
            print(f"Error sending: {e}")

    def send_code(self, email):
        verification_code = self.generate_verification_code()
        self.send_email(email, verification_code)
        return verification_code

    def send_leave_request_email(self, full_name, leave_type, text):
        subject = f"{full_name} - {leave_type} Request"

        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.sender_email
        message["Subject"] = subject
        message.attach(MIMEText(text, "plain"))

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.ukr.net", 465, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.sender_email, message.as_string())
            print(f"Leave request email successfully sent.")
        except Exception as e:
            print(f"Error sending leave request email: {e}")


