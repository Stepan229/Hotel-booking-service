from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

urlpatterns = [
    path("<int:hotel_id>/", RoomViews.as_view({'get': 'list'}),
         name='rooms-list-in-hotel'),
    path("", RoomViews.as_view({'post': 'create'}),
         name='rooms-add-in-hotel'),
]