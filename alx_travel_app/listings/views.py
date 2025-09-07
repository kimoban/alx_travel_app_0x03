# Paystack payment integration
from .paystack import initialize_transaction, verify_transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from listings.tasks import send_booking_confirmation_email

class PaystackInitPaymentView(APIView):
    def post(self, request):
        email = request.data.get("email")
        amount = request.data.get("amount")
        reference = request.data.get("reference")
        if not email or not amount or not reference:
            return Response({"error": "email, amount, and reference are required."}, status=400)
        result = initialize_transaction(email, float(amount), reference)
        return Response(result)

class PaystackVerifyPaymentView(APIView):
    def get(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"error": "reference is required."}, status=400)
        result = verify_transaction(reference)
        return Response(result)
from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        # Generate a unique reference for Paystack
        import uuid
        reference = f"booking_{booking.pk}_{uuid.uuid4().hex[:8]}"
        booking.paystack_reference = reference
        # Initiate Paystack payment
        result = initialize_transaction(booking.user.email, float(booking.total_price), reference)
        payment_url = None
        if result.get('status') and result.get('data'):
            payment_url = result['data'].get('authorization_url')
        booking.save()
        # Optionally, send booking confirmation email
        try:
            send_booking_confirmation_email.delay(booking.pk) # type: ignore
        except Exception:
            pass
        # Attach payment_url to the booking instance for response
        booking._payment_url = payment_url


# Payment endpoints for Chapa integration
import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment, Booking
from .serializers import PaymentSerializer

class InitiatePaymentView(APIView):
    def post(self, request):
        booking_id = request.data.get('booking_id')
        amount = request.data.get('amount')
        if not booking_id or not amount:
            return Response({'error': 'booking_id and amount are required.'}, status=400)
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=404)

        chapa_key = os.environ.get('CHAPA_SECRET_KEY') or getattr(settings, 'CHAPA_SECRET_KEY', None)
        if not chapa_key:
            return Response({'error': 'Chapa secret key not configured.'}, status=500)

        # Prepare Chapa API request
        chapa_url = 'https://api.chapa.co/v1/transaction/initialize'
        headers = {'Authorization': f'Bearer {chapa_key}'}
        data = {
            'amount': amount,
            'currency': 'ETB',
            'email': request.data.get('email', 'test@example.com'),
            'first_name': request.data.get('first_name', 'Test'),
            'last_name': request.data.get('last_name', 'User'),
            'tx_ref': f'booking_{booking_id}_{booking.user.pk}',
            'callback_url': request.build_absolute_uri('/api/payments/verify/'),
            'return_url': request.build_absolute_uri('/api/payments/verify/'),
        }
        chapa_response = requests.post(chapa_url, json=data, headers=headers)
        if chapa_response.status_code != 200:
            return Response({'error': 'Failed to initiate payment with Chapa.', 'details': chapa_response.json()}, status=502)
        chapa_data = chapa_response.json().get('data', {})
        transaction_id = chapa_data.get('tx_ref')
        payment_url = chapa_data.get('checkout_url')
        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            transaction_id=transaction_id,
            status='Pending',
        )
        serializer = PaymentSerializer(payment)
        return Response({'payment': serializer.data, 'payment_url': payment_url}, status=201)


class VerifyPaymentView(APIView):
    def get(self, request):
        tx_ref = request.query_params.get('tx_ref')
        if not tx_ref:
            return Response({'error': 'tx_ref is required.'}, status=400)
        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=404)

        chapa_key = os.environ.get('CHAPA_SECRET_KEY') or getattr(settings, 'CHAPA_SECRET_KEY', None)
        if not chapa_key:
            return Response({'error': 'Chapa secret key not configured.'}, status=500)

        chapa_url = f'https://api.chapa.co/v1/transaction/verify/{tx_ref}'
        headers = {'Authorization': f'Bearer {chapa_key}'}
        chapa_response = requests.get(chapa_url, headers=headers)
        if chapa_response.status_code != 200:
            return Response({'error': 'Failed to verify payment with Chapa.', 'details': chapa_response.json()}, status=502)
        chapa_data = chapa_response.json().get('data', {})
        status_str = chapa_data.get('status')
        if status_str == 'success':
            payment.status = 'Completed'
            payment.save()
            # Send payment confirmation email asynchronously
            from listings.tasks import send_payment_confirmation_email # type: ignore
            send_payment_confirmation_email.delay(payment.booking.pk)
        else:
            payment.status = 'Failed'
            payment.save()
        serializer = PaymentSerializer(payment)
        return Response({'payment': serializer.data, 'chapa_status': status_str})
