from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import HotelCatalog, RoomCatalog, RoomBooking
from . import serializers
from .utils import sorted_by_field, delete_entity_by_id 


class HotelViewSet(viewsets.GenericViewSet):
    queryset = HotelCatalog.objects.all()

    permission_classes = [AllowAny, ]
    serializer_class = serializers.HotelSerializer

    def list(self, request, *args, **kwargs):
        hotels = self.get_queryset()
        data = self._get_hotel_data(hotels)
        if not data:
            return Response("No hotels found.",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(data=data, status=status.HTTP_200_OK)

    def _get_hotel_data(self, hotels):
        serializer = self.get_serializer(hotels, many=True)
        return serializer.data
    
    @action(methods=['POST', ], detail=False)
    def create_hotel(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'id': serializer.data['id']}, status=status.HTTP_201_CREATED)

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
        try:
            rooms = self._apply_room_sorting(request, self.get_queryset())
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
        data = self._get_room_data(rooms)
        if not data:
            return Response(f"Room number {self.kwargs.get('hotel_id', None)} was not found",
                             status=status.HTTP_404_NOT_FOUND)
        
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def create_room(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'id': serializer.data['id']}, status=status.HTTP_201_CREATED)


    @action(methods=['Delete', ], detail=False)
    def delete_room(self, request, *args, **kwargs):
        room_id = self.kwargs.get('pk', None)
        if not self._delete_room(room_id):
            return Response(f"Room number {room_id} was not found",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    

    def _delete_room(self, room_id):
        return delete_entity_by_id(self.get_queryset(), room_id)
    
    def _apply_room_sorting(self, request, rooms):
        sort = request.GET.get('sort', None)
        rooms = sorted_by_field(rooms, ['price', 'created_at'], sort)
        return rooms
    
    def _get_room_data(self, room):
        serializer = self.get_serializer(room, many=True)
        return serializer.data

    
class BookingRoomViewSet(viewsets.GenericViewSet):
    queryset = RoomBooking.objects.all()

    permission_classes = [AllowAny, ]
    serializer_class = serializers.RoomBookingSerializer

    def list(self, request):
        reservations = self._get_reservations(request)
        room_reservations_sorted = self._apply_reservation_sorting(reservations)
        data = self._get_reservations_data(room_reservations_sorted)
        if not data:
            return Response("No reservations found for the specified room.",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(data=data, status=status.HTTP_200_OK)



    @action(methods=['POST', ], detail=False)
    def create_reservation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data['id'], status=status.HTTP_201_CREATED)


    @action(methods=['DELETE', ], detail=False)
    def delete_reservation(self, request, *args, **kwargs):
        if not self._delete_reservation():
            return Response(f"Reservation {self.kwargs.get('pk', None)} was not found",
                            status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    
    def _delete_reservation(self):
        queryset = self.get_queryset()
        reservation_id = self.kwargs.get('pk', None)
        return delete_entity_by_id(queryset, reservation_id)
    
    def _get_reservations(self, request):
        room = request.GET.get('room_id', None)
        reservations = self.get_queryset().filter(room=room)
        return reservations
    
    def _get_reservations_data(self, reservations):
        serializer = self.get_serializer(reservations, many=True)
        return serializer.data

    def _apply_reservation_sorting(self, reservations):
        return sorted_by_field(reservations, ['date_start', 'date_end', 'created_at'], 'date_start')
        