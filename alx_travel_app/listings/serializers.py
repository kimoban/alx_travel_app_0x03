from rest_framework import serializers
from .models import Listing, Booking

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    payment_url = serializers.SerializerMethodField(read_only=True)

    def get_payment_url(self, obj):
        # Return the payment_url if present (set in viewset)
        return getattr(obj, '_payment_url', None)

    class Meta:
        model = Booking
        fields = '__all__'
        extra_fields = ['payment_url']
        read_only_fields = ['payment_url']


# Payment serializer
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
