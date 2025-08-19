from twilio.rest import Client
import os
import smtplib
import ssl
import certifi

class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.
    def __init__(self):
        self.smtp_address=os.environ['EMAIL_PROVIDER_SMTP_ADDRESS']
        self.email=os.environ['MY_EMAIL']
        self.email_password=os.environ['MY_EMAIL_PASSWORD']
        self.twilio_verified_number=os.environ['TWILIO_VERIFIED_NUMBER']
        self.whatsapp_number=os.environ['TWILIO_WHATSAPP_NUMBER']
        self.client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
        # self.connection=smtplib.SMTP(host=os.environ["EMAIL_PROVIDER_SMTP_ADDRESS"],port=587, timeout=30)
        self.smtp_host=os.environ['EMAIL_PROVIDER_SMTP_ADDRESS']
        self.smtp_port=587

    def send_emails(self,email_list, email_body):
        # with self.connection:
        #     self.connection.starttls()
        #     self.connection.login(self.email, self.email_password)
        #     for email in email_list:
        #         self.connection.sendmail(
        #             from_addr=self.email,
        #             to_addrs=email,
        #             msg=f"Subject: AirAlert - New Low Price Flight!\n\n{email_body}".encode("utf-8")
        #     )
        subject = "AirAlert - New Low Price Flight!"
        ctx = ssl.create_default_context(cafile=certifi.where())

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as conn:
            conn.ehlo()
            conn.starttls(context=ctx)  # ← use certifi bundle
            conn.ehlo()
            conn.login(self.email, self.email_password)

            for rcpt in email_list:
                msg = (
                    f"Subject: {subject}\n"
                    f"From: {self.email}\n"
                    f"To: {rcpt}\n"
                    f"Content-Type: text/plain; charset=utf-8\n\n"
                    f"{email_body}"
                )
                conn.sendmail(self.email, rcpt, msg.encode("utf-8"))


    def send_whatsapp(self, message_body):
            message = self.client.messages.create(
                from_=f'whatsapp:{os.environ["TWILIO_WHATSAPP_NUMBER"]}',
                body=message_body,
                to=f'whatsapp:{os.environ["TWILIO_VERIFIED_NUMBER"]}'
            )
            print(message.sid)