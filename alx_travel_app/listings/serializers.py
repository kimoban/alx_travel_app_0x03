from rest_framework import serializers
from .models import Listing, Booking, Review
from .models import Payment
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['transaction_id', 'status', 'created_at', 'updated_at']
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['host', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'total_price', 'created_at', 'updated_at']
    
    def validate_listing_id(self, value):
        """Validate that the listing exists and is active."""
        try:
            listing = Listing.objects.get(id=value, is_active=True)
            return value
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing not found or not active.")
    
    def validate(self, attrs):
        """Validate booking dates."""
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        
        # Check for overlapping bookings
        listing_id = attrs['listing_id']
        overlapping_bookings = Booking.objects.filter(
            listing_id=listing_id,
            status='confirmed',
            start_date__lt=attrs['end_date'],
            end_date__gt=attrs['start_date']
        )
        
        if self.instance:
            overlapping_bookings = overlapping_bookings.exclude(id=self.instance.id)
        
        if overlapping_bookings.exists():
            raise serializers.ValidationError("These dates are not available for booking.")
        
        return attrs
    
    def create(self, validated_data):
        """Create booking with the listing."""
        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(id=listing_id)
        validated_data['listing'] = listing
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    listing_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_listing_id(self, value):
        """Validate that the listing exists."""
        try:
            Listing.objects.get(id=value)
            return value
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing not found.")
    
    def validate_rating(self, value):
        """Validate that rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        """Create review with the listing."""
        listing_id = validated_data.pop('listing_id')
        listing = Listing.objects.get(id=listing_id)
        validated_data['listing'] = listing
        return super().create(validated_data)