from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import HotelCatalog, RoomCatalog, RoomBooking
from . import serializers
# import .serializers


# Create your views here.
class RoomViews(viewsets.GenericViewSet):
    queryset = RoomCatalog.objects.all()

    permission_classes = [AllowAny, ]
    serializer_class = serializers.RoomSerializer
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        print()


    def list(self, request, *args, **kwargs):
        print('HOTEL ', request.data)
        id_hotel = int(self.kwargs.get('hotel_id'))
        rooms = HotelCatalog.objects.filter(hotel=id_hotel)
        serializer = self.get_serializer(rooms, many=True)
        print(serializer.data, 'HOTEL ')
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def create(self, request):
        data = dict(request.data)
        del data['csrfmiddlewaretoken']
        print(data)
        queryset = RoomCatalog.objects.all()
        serializer = self.get_serializer(data=[data], many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer.validated_data, 'HOTEL ')
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        