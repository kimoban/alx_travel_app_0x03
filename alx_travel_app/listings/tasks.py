from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from listings.models import Booking

def get_booking_email_content(booking_id):
    try:
        booking = Booking.objects.select_related('user', 'listing').get(id=booking_id)
        subject = f"Booking Confirmation for {booking.listing.title}"
        message = (
            f"Dear {booking.user.first_name},\n\n"
            f"Your booking for {booking.listing.title} from {booking.start_date} to {booking.end_date} has been confirmed.\n"
            f"Total Price: {booking.total_price}\n\nThank you for booking with us!"
        )
        recipient = [booking.user.email]
        return subject, message, recipient
    except Booking.DoesNotExist:
        return None, None, None


@shared_task
def send_booking_confirmation_email(booking_id):
    subject, message, recipient = get_booking_email_content(booking_id)
    if subject and recipient:
        send_mail(
            subject,
            message or "",
            settings.DEFAULT_FROM_EMAIL,
            recipient,
            fail_silently=False,
        )


# Payment confirmation email task
@shared_task
def send_payment_confirmation_email(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return 'Booking not found.'
    user_email = booking.user.email if hasattr(booking.user, 'email') else None
    if not user_email:
        return 'No email found for user.'
    subject = 'Payment Confirmation'
    message = f'Your payment for booking {booking.pk} has been confirmed. Thank you!'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
    return 'Email sent.'
