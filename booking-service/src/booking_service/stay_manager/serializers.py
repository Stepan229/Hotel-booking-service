from rest_framework import serializers
from .models import HotelCatalog, RoomCatalog, RoomBooking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCatalog
        fields = '__all__'

    def create(self, validated_data):
        print('Validate ', validated_data)
        room = model.objects.create(room_description=validated_data['room_description'], 
                                        price=validated_data['price'], 
                                        hotel=validated_data['hotel'])
        return room