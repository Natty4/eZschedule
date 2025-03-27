from rest_framework import serializers
from cloudinary.models import CloudinaryField

class CloudinaryURLField(serializers.Field):
    def to_representation(self, value):
        """
        Return the Cloudinary URL for a CloudinaryField.
        """
        if isinstance(value, CloudinaryField):
            return value.url if value else None
        return None
