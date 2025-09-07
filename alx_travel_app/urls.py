# alx_travel_app/urls.py

"""
URL configuration for alx_travel_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from .views import welcome

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="ALXbnb Travel API",
        default_version="v1",
        description="A modern travel and booking API inspired by Airbnb.\n\nFeatures: Listings, Bookings, Payments, User Auth, and more.",
        contact=openapi.Contact(email="support@alxbnb.com", name="ALXbnb Support", url="https://alx-travel-app-web.onrender.com/"),
        license=openapi.License(name="MIT License"),
        x_logo={"url": "/static/branding/logo.png", "altText": "ALXbnb Logo"},
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("listings.urls")),
    path("", welcome, name="welcome"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("accounts/", include("django.contrib.auth.urls")),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)