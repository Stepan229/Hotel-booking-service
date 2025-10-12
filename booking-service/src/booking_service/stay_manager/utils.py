from rest_framework.response import Response

def sorted_by_field(queryset, possible_fields_name, field_name):
    """
    Sorts a queryset by the specified field name if it exists in the model.
    """
    possible_sorting = possible_fields_name + list(map(lambda x: f"-{x}", possible_fields_name))
    if not field_name:
        return queryset
    if field_name not in possible_sorting:  
        raise ValueError(f"Sorting by {field_name} is not allowed. Use {possible_fields_name} fields.")
    return queryset.order_by(field_name)

def delete_room(queryset, room_id):
    """
    Deletes a room with the specified ID from the given queryset.
    Args:
        queryset: A Django QuerySet containing room objects.
        room_id (int): The ID of the room to be deleted.
    Returns:
        bool: True if the room was successfully deleted, False if the room does not exist.
    """
    return delete_entity_by_id(queryset, room_id)

def delete_entity_by_id(queryset, entity_id):
    """
    Deletes an entity with the specified ID from the given queryset.
    Args:
        queryset: A Django QuerySet containing entity objects.
        entity_id (int): The ID of the entity to be deleted.
    Returns:
        bool: True if the entity was successfully deleted, False if the entity does not exist.
    """
    try:
        obj = queryset.get(id=entity_id)
        obj.delete()
    except queryset.model.DoesNotExist:
        return False
    return True
    
