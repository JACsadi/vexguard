import random
import requests
import smtplib
from email.message import EmailMessage
def generate_message():
    return "matha"
def send_otp_sms(phone_number, otp_code, api_key, api_url):
    payload = {
        'api_key': api_key,
        'msg': f"Your OTP is: {otp_code}. Do not share this code.",
        'to': phone_number
    }
    try:
        response = requests.post(api_url, data=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return None

    # Example Usage (replace with your actual details)
API_KEY = "KZKj3686njM7z4V1Ed7WDnS8uAdYAXFpEbO4VI8J"
SMS_API_URL = "https://api.sms.net.bd/sendsms" # Example for sms.net.bd

user_phone_number = "8801792624255" # Replace with recipient's number
otp = generate_message()

print(f"Generated OTP: {otp}")
send_result = send_otp_sms(user_phone_number, otp, API_KEY, SMS_API_URL)

if send_result:
    print("SMS sent successfully:", send_result)
else:
    print("Failed to send SMS.")

# send_simple.py

