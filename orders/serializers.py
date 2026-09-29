from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity']

    # Custom validation for quantity to provide a useful error message
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    # allow_empty=False prevents someone from sending an empty items array
    items = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'items']

    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("An order must contain at least one product.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order