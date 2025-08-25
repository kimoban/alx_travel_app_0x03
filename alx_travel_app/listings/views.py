from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
import os
import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import QuerySet

# Chapa Payment Initiation Endpoint
class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        amount = request.data.get('amount')
        user = request.user
        if not booking_id or not amount:
            return Response({'error': 'booking_id and amount are required.'}, status=400)
        try:
            booking = Booking.objects.get(id=booking_id, user=user)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=404)

        chapa_key = os.environ.get('CHAPA_SECRET_KEY') or getattr(settings, 'CHAPA_SECRET_KEY', None)
        if not chapa_key:
            return Response({'error': 'Chapa secret key not configured.'}, status=500)

        url = 'https://api.chapa.co/v1/transaction/initialize'
        headers = {'Authorization': f'Bearer {chapa_key}'}
        data = {
            'amount': amount,
            'currency': 'ETB',
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tx_ref': f'booking_{booking_id}_{user.id}',
            'callback_url': request.build_absolute_uri('/api/payments/verify/'),
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200 and response.json().get('status') == 'success':
            chapa_data = response.json()['data']
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                transaction_id=chapa_data['tx_ref'],
                status='pending',
            )
            return Response({
                'payment': PaymentSerializer(payment).data,
                'checkout_url': chapa_data['checkout_url'],
            }, status=201)
        return Response({'error': 'Failed to initiate payment.', 'details': response.json()}, status=400)


# Chapa Payment Verification Endpoint
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tx_ref = request.query_params.get('tx_ref')
        if not tx_ref:
            return Response({'error': 'tx_ref is required.'}, status=400)
        try:
            payment = Payment.objects.get(transaction_id=tx_ref, booking__user=request.user)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=404)

        chapa_key = os.environ.get('CHAPA_SECRET_KEY') or getattr(settings, 'CHAPA_SECRET_KEY', None)
        if not chapa_key:
            return Response({'error': 'Chapa secret key not configured.'}, status=500)

        url = f'https://api.chapa.co/v1/transaction/verify/{tx_ref}'
        headers = {'Authorization': f'Bearer {chapa_key}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json().get('status') == 'success':
            chapa_status = response.json()['data']['status']
            if chapa_status == 'success':
                payment.status = 'completed'
            else:
                payment.status = 'failed'
            payment.save()
            return Response({'payment': PaymentSerializer(payment).data, 'chapa_status': chapa_status})
        return Response({'error': 'Failed to verify payment.', 'details': response.json()}, status=400)

@api_view(['GET'])
def index(request):
    return Response({"message": "Welcome to ALX Travel App API"})

class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listings.
    Provides CRUD operations for Listing model.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    
    def perform_create(self, serializer):
        """Set the host to the current user when creating a listing."""
        serializer.save(host=self.request.user)
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific listing."""
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific listing."""
        listing = self.get_object()
        reviews = listing.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    Provides CRUD operations for Booking model.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def perform_create(self, serializer):
        """Set the user to the current user and calculate total price when creating a booking."""
        listing = serializer.validated_data['listing']
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        
        # Calculate the number of nights
        nights = (end_date - start_date).days
        total_price = nights * listing.price_per_night
        
        serializer.save(user=self.request.user, total_price=total_price)
    def get_queryset(self): # type: ignore
        """Filter bookings to show only the current user's bookings."""
        if self.request.user.is_authenticated:
            return Booking.objects.filter(user=self.request.user)
        return Booking.objects.none()

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.
    Provides CRUD operations for Review model.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating a review."""
        serializer.save(user=self.request.user)
    
    def get_queryset(self) -> QuerySet: # type: ignore
        """Filter reviews to show only the current user's reviews."""
        if self.request.user.is_authenticated:
            return Review.objects.filter(user=self.request.user)
        return Review.objects.none()
