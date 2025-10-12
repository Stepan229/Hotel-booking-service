from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import HotelCatalog, RoomCatalog, RoomBooking
from . import serializers
# import .serializers


# Create your views here.
class RoomViewSet(viewsets.GenericViewSet):
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
        
        sort = request.GET.get('sort', None)
        if sort:
            if sort not in ['price', '-price', 'created_at', '-created_at']:
                return Response(f"Sorting by {sort} is not allowed. Use 'price' or 'created_at' fields.",
                                status=status.HTTP_400_BAD_REQUEST)
            rooms = rooms.order_by(sort)
    
        serializer = self.get_serializer(rooms, many=True)
        if not serializer.data:
            return Response(f"Room number {self.kwargs.get('hotel_id', None)} was not found",
                             status=status.HTTP_404_NOT_FOUND)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def create_room(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data['id'], status=status.HTTP_201_CREATED)


    @action(methods=['Delete', ], detail=False)
    def delete_room(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        room_id = self.kwargs.get('pk', None)
        try:
            room = queryset.get(id=room_id)
            room.delete()
        except RoomCatalog.DoesNotExist:
            return Response(f"Room number {room_id} was not found",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    
class BookingRoomViewSet(viewsets.GenericViewSet):
    queryset = RoomBooking.objects.all()

    permission_classes = [AllowAny, ]
    serializer_class = serializers.RoomBookingSerializer

    def list(self, request):
        room = request.GET.get('room_id', None)
        room_reservations = self.get_queryset().filter(room=room)
        serializer = self.get_serializer(room_reservations, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def create_reservation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data['id'], status=status.HTTP_201_CREATED)


    @action(methods=['Delete', ], detail=False)
    def delete_reservation(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        room_id = self.kwargs.get('pk', None)
        try:
            reservation = queryset.get(id=room_id)
            reservation.delete()
        except RoomCatalog.DoesNotExist:
            return Response(f"Reservation {room_id} was not found",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_205_RESET_CONTENT)
        