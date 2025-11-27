# app/emailer.py
import smtplib
from email.message import EmailMessage
from .config import SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_USE_TLS, EMAIL_FROM_NAME


class Emailer:
    @staticmethod
    def send_email(to_address: str, subject: str, body: str):
        """
        Send email to recipient.
        to_address: recipient email (user's email from database)
        subject: email subject
        body: email body (plain text)
        """
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = f"{EMAIL_FROM_NAME} <{SMTP_USERNAME}>"
            msg['To'] = to_address
            msg.set_content(body)

            # Connect to SMTP server
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                if EMAIL_USE_TLS:
                    server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            print(f"✅ Email sent to {to_address}")
            return {"success": True}

        except Exception as e:
            print(f"❌ Email failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_document_approved_email(recipient_email: str, resident_name: str):
        """Email template: Document approved"""
        subject = "Document Verification - Approved ✅"
        body = f"""
Good day, {resident_name}!

We are pleased to inform you that your uploaded documents have been verified and approved by our office.

You may now proceed to create your account and access our Barangay E-Services system.

If you have any questions, please visit Barangay Balibago Hall or contact us. 

Sincerely,
Barangay Balibago E-Services Team
Barangay Balibago, Calatagan, Batangas
        """
        return Emailer.send_email(recipient_email, subject, body)

    @staticmethod
    def send_document_rejected_email(recipient_email: str, resident_name: str, reason: str):
        """Email template: Document rejected"""
        subject = "Document Verification - Action Required ❌"
        body = f"""
Good day, {resident_name}!

We regret to inform you that your uploaded documents require correction.

Reason for rejection:
{reason}

Please re-upload the correct documents to proceed with your registration.

If you need assistance, please visit Barangay Balibago Hall. 

Sincerely,
Barangay Balibago E-Services Team
Barangay Balibago, Calatagan, Batangas
        """
        return Emailer.send_email(recipient_email, subject, body)

    @staticmethod
    def send_payment_verified_email(recipient_email: str, resident_name: str, service_name: str, amount: float):
        """Email template: Payment verified"""
        subject = "Payment Verified - Request Approved ✅"
        body = f"""
Good day, {resident_name}!

Your payment of ₱{amount:. 2f} for {service_name} has been verified and approved.

Your request is now being processed. You will receive another notification once your document is ready for pickup.

Thank you for using our E-Services! 

Sincerely,
Barangay Balibago E-Services Team
Barangay Balibago, Calatagan, Batangas
        """
        return Emailer.send_email(recipient_email, subject, body)

    @staticmethod
    def send_document_ready_email(recipient_email: str, resident_name: str, service_name: str, pickup_date: str):
        """Email template: Document ready for pickup"""
        subject = "Document Ready for Pickup 📄"
        body = f"""
Good day, {resident_name}!

Your requested document ({service_name}) is now ready for pickup! 

Pickup Schedule:
Date: {pickup_date}
Location: Barangay Balibago Hall, Calatagan, Batangas

Please bring a valid ID when claiming your document.

Office Hours: Monday to Friday, 8:00 AM - 5:00 PM

Thank you for using our E-Services! 

Sincerely,
Barangay Balibago E-Services Team
Barangay Balibago, Calatagan, Batangas
        """
        return Emailer.send_email(recipient_email, subject, body)

    @staticmethod
    def send_request_status_update_email(recipient_email: str, resident_name: str, service_name: str, status: str):
        """Email template: Request status update"""
        subject = f"Request Status Update - {status}"
        body = f"""
Good day, {resident_name}! 

Your request for {service_name} has been updated. 

Current Status: {status}

You can log in to the Barangay E-Services system to view more details.

If you have any questions, please contact Barangay Balibago Hall.

Sincerely,
Barangay Balibago E-Services Team
Barangay Balibago, Calatagan, Batangas
        """
        return Emailer.send_email(recipient_email, subject, body)