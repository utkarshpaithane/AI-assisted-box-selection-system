from rest_framework import serializers
from .models import Product, Box

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' # This automatically includes all fields from the model (id, name, length, etc.)

class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = '__all__'