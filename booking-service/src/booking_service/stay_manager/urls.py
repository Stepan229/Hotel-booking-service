from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

urlpatterns = [
     path("hotels/<int:hotel_id>/rooms/", RoomViewSet.as_view({'get': 'list'}),
                                                  name='hotel-list-rooms'),
     path("rooms/", RoomViewSet.as_view({'post': 'create_room'}),
                                                  name='hotel-rooms'),
     path("rooms/<int:pk>/", RoomViewSet.as_view({'delete': 'delete_room'}),
                                                   name='room-detail'),

     path("bookings/list/", BookingRoomViewSet.as_view({'get': 'list'}),
                                                  name='booking-list-reservations'),
     path("bookings/create/", BookingRoomViewSet.as_view({'post': 'create_reservation'}),
                                                  name='booking-create-reservation'),
     path("bookings/<int:pk>/", BookingRoomViewSet.as_view({'delete': 'delete_reservation'}),
                                                  name='booking-delete-reservation'),                                                   
]