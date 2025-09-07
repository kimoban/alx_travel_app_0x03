from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, InitiatePaymentView, VerifyPaymentView, PaystackInitPaymentView, PaystackVerifyPaymentView

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/payments/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('api/payments/verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('api/paystack/init/', PaystackInitPaymentView.as_view(), name='paystack-init'),
    path('api/paystack/verify/', PaystackVerifyPaymentView.as_view(), name='paystack-verify'),
]
