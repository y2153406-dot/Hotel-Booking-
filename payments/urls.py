from django.urls import path

from . import views


urlpatterns = [

    path(
        'create/<int:booking_id>/',
        views.create_payment,
        name='create_payment'
    ),


    path(
        'verify/<int:booking_id>/',
        views.verify_payment,
        name='verify_payment'
    ),

]