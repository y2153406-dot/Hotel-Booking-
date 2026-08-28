from django.urls import path
from . import views


urlpatterns = [
    path(
        'create/<int:room_id>/',
        views.create_booking,
        name='create_booking'
    ),
]