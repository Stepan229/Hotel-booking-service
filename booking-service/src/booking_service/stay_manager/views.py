from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import HotelCatalog, RoomCatalog, RoomBooking
from . import serializers
# import .serializers


# Create your views here.
class RoomViewsSet(viewsets.GenericViewSet):
    queryset = RoomCatalog.objects.all()

    permission_classes = [AllowAny, ]
    serializer_class = serializers.RoomSerializer
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        hotel_id = self.kwargs.get('hotel_id', None)
        queryset = super().get_queryset()

        if hotel_id and hotel_id is not None:
            hotel_id = int(hotel_id)
            try:
                hotel = HotelCatalog.objects.get(id=hotel_id)
                return queryset.filter(hotel=hotel)
            except HotelCatalog.DoesNotExist:
                return RoomCatalog.objects.none()
        return queryset

    def list(self, request, *args, **kwargs):
        rooms = self.get_queryset()
        serializer = self.get_serializer(rooms, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def create_room(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data['id'], status=status.HTTP_201_CREATED)


    @action(methods=['Delete', ], detail=False)
    def delete_room(self, request):
        queryset = self.get_queryset()
        try:
            room = queryset.get(id=request.data['id'])
            room.delete()
        except RoomCatalog.DoesNotExist:
            return Response(f"Room number {request.data['id']} was not found",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    
class BookingRoomViewsSet(viewsets.GenericViewSet):
    queryset = RoomBooking.objects.all()

    permission_classes = [AllowAny, ]
    serializer_class = serializers.RoomSerializer

    def list(self, request, *args, **kwargs):
        room = self.kwargs.get('room_id',)
        room_reservations = self.get_queryset().filter(room=room)
        serializer = self.get_serializer(room_reservations, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def create_room(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data['id'], status=status.HTTP_201_CREATED)


    @action(methods=['Delete', ], detail=False)
    def delete_room(self, request):
        queryset = self.get_queryset()
        try:
            room = queryset.get(id=request.data['id'])
            room.delete()
        except RoomCatalog.DoesNotExist:
            return Response(f"Room number {request.data['id']} was not found",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_205_RESET_CONTENT)
        