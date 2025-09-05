from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
import random
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        self.create_users()
        self.create_listings()
        self.create_bookings()
        self.create_reviews()
        self.stdout.write(self.style.SUCCESS('Successfully seeded data!'))

    def create_users(self):
        if not User.objects.filter(username='host1').exists():
            User.objects.create_user(
                username='host1',
                email='host1@example.com',
                password='testpass123',
                first_name='John',
                last_name='Doe'
            )
        
        if not User.objects.filter(username='guest1').exists():
            User.objects.create_user(
                username='guest1',
                email='guest1@example.com',
                password='testpass123',
                first_name='Jane',
                last_name='Smith'
            )

    def create_listings(self):
        host = User.objects.get(username='host1')
        property_types = [choice[0] for choice in Listing.PROPERTY_TYPES]
        
        listings_data = [
            {
                'title': 'Cozy Apartment in Downtown',
                'description': 'A beautiful apartment in the heart of the city',
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'price_per_night': 120.00,
                'property_type': 'apartment',
                'num_bedrooms': 2,
                'num_bathrooms': 1,
                'max_guests': 4,
                'amenities': 'WiFi, Kitchen, TV, Air Conditioning',
                'host': host
            },
            {
                'title': 'Luxury Villa with Pool',
                'description': 'Stunning villa with private pool and ocean view',
                'address': '456 Beach Rd',
                'city': 'Miami',
                'state': 'FL',
                'country': 'USA',
                'price_per_night': 350.00,
                'property_type': 'villa',
                'num_bedrooms': 4,
                'num_bathrooms': 3,
                'max_guests': 8,
                'amenities': 'Pool, WiFi, Kitchen, TV, Air Conditioning, Parking',
                'host': host
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Peaceful cabin in the woods with mountain views',
                'address': '789 Forest Ln',
                'city': 'Aspen',
                'state': 'CO',
                'country': 'USA',
                'price_per_night': 180.00,
                'property_type': 'cabin',
                'num_bedrooms': 3,
                'num_bathrooms': 2,
                'max_guests': 6,
                'amenities': 'Fireplace, Kitchen, Hot Tub, WiFi',
                'host': host
            }
        ]

        for listing_data in listings_data:
            if not Listing.objects.filter(title=listing_data['title']).exists():
                Listing.objects.create(**listing_data)

    def create_bookings(self):
        guest = User.objects.get(username='guest1')
        listings = Listing.objects.all()
        
        for listing in listings:
            if not Booking.objects.filter(listing=listing, user=guest).exists():
                start_date = datetime.now() + timedelta(days=random.randint(1, 30))
                end_date = start_date + timedelta(days=random.randint(1, 14))
                total_price = (end_date - start_date).days * listing.price_per_night
                
                Booking.objects.create(
                    listing=listing,
                    user=guest,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_price
                )

    def create_reviews(self):
        guest = User.objects.get(username='guest1')
        bookings = Booking.objects.filter(user=guest)
        
        for booking in bookings:
            if not Review.objects.filter(listing=booking.listing, user=guest).exists():
                Review.objects.create(
                    listing=booking.listing,
                    user=guest,
                    rating=random.randint(3, 5),
                    comment=f"Great stay at {booking.listing.title}! Everything was as described."
                )