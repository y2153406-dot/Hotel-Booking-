from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'room',
        'check_in',
        'check_out',
        'guests',
        'total_price',
        'status',
        'created_at',
    )


    list_filter = (
        'status',
        'check_in',
        'check_out',
    )


    search_fields = (
        'user__username',
        'room__hotel__name',
        'room__room_type',
    )


    list_editable = (
        'status',
    )


    ordering = (
        '-created_at',
    )