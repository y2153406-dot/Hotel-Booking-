from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),

    path('hotels/', include('hotels.urls')),

    path('bookings/', include('bookings.urls')),

    # Our accounts URLs
    path('accounts/', include('accounts.urls')),

    # django-allauth URLs
    path('accounts/', include('allauth.urls')),
    path(
    'payments/',
    include('payments.urls')
),
]


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )