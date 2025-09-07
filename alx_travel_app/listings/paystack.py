import requests
from django.conf import settings

def initialize_transaction(email, amount, reference):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": int(amount * 100),  # Paystack expects amount in kobo
        "reference": reference,
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def verify_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    return response.json()
