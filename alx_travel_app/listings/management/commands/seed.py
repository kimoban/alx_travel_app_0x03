from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = 'Seed the database with sample listings.'

    def handle(self, *args, **kwargs):
        sample_listings = [
            {
                'title': 'Cozy Apartment',
                'description': 'A nice and cozy apartment in the city center.',
                'location': 'Lagos',
                'price_per_night': 100.00,
            },
            {
                'title': 'Beach House',
                'description': 'A beautiful house by the beach.',
                'location': 'Accra',
                'price_per_night': 200.00,
            },
            {
                'title': 'Mountain Cabin',
                'description': 'A peaceful cabin in the mountains.',
                'location': 'Kigali',
                'price_per_night': 150.00,
            },
        ]
        for data in sample_listings:
            obj, created = Listing.objects.get_or_create(title=data['title'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created listing: {obj.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Listing already exists: {obj.title}"))
