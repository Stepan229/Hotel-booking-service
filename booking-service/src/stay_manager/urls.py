from django.urls import path

from .views import RoomViewSet, BookingRoomViewSet, HotelViewSet

urlpatterns = [
     path("hotels/<int:hotel_id>/rooms/", RoomViewSet.as_view({'get': 'list'}),
                                                  name='list-rooms'),
     path("rooms/create/", RoomViewSet.as_view({'post': 'create_room'}),
                                                  name='rooms-create'),
     path("rooms/<int:pk>/", RoomViewSet.as_view({'delete': 'delete_room'}),
                                                   name='room-detail'),

     path("bookings/list/", BookingRoomViewSet.as_view({'get': 'list'}),
                                                  name='booking-list-reservations'),
     path("bookings/create/", BookingRoomViewSet.as_view({'post': 'create_reservation'}),
                                                  name='booking-create-reservation'),
     path("bookings/<int:pk>/", BookingRoomViewSet.as_view({'delete': 'delete_reservation'}),
                                                  name='booking-delete-reservation'),   
     path("hotels/create/", HotelViewSet.as_view({'post': 'create_hotel'}),
                                                  name='hotel-create'),
     path("hotels/list/", HotelViewSet.as_view({'get': 'list'}),
                                                  name='hotel-list'),                                                 
]