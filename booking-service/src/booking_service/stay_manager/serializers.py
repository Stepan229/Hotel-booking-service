from rest_framework import serializers
from .models import HotelCatalog, RoomCatalog, RoomBooking

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelCatalog
        fields = '__all__'
        


class RoomSerializer(serializers.ModelSerializer):
    hotel = serializers.PrimaryKeyRelatedField(
        queryset=HotelCatalog.objects.all()
    )
    class Meta:
        model = RoomCatalog
        fields = '__all__'

    # def create(self, validated_data):
    #     print('Hotel: ', type(validated_data['hotel']))
    #     room = RoomCatalog.objects.create(room_description=validated_data['room_description'], 
    #                                     price=validated_data['price'], 
    #                                     hotel=validated_data['hotel'])
    #     return room