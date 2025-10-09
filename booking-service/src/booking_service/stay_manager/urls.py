from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

urlpatterns = [
     path("<int:hotel_id>/", RoomViews.as_view({'get': 'list'}),
                                                  name='hotel-list-rooms'),
     path("", RoomViews.as_view({'post': 'create_room',
                                                  'delete': 'delete_room'}),
                                                  name='hotel-rooms'),
]