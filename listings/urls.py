from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    # Include the router URLs
    path('', include(router.urls)),
    path('payments/initiate/', views.InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payments/verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
]
