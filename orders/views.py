from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .services import BoxRecommendationService

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Nested order updates aren't supported, so PUT/PATCH are disabled (would crash with a 500)
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    # The @action decorator creates a custom endpoint for this ViewSet
    # detail=True means this action applies to a specific order ID (e.g., /api/orders/1/...)
    @action(detail=True, methods=['post'], url_path='recommend-box')
    def recommend_box(self, request, pk=None):
        # 1. Fetch the order from the database
        order = self.get_object()
        
        # 2. Get all items related to this order
        order_items = order.items.all()
        
        if not order_items.exists():
            return Response({"error": "This order has no items."}, status=400)

        # 3. Call our service algorithm
        best_box, total_weight, reason, other_boxes = BoxRecommendationService.recommend_box(order_items)
        
        # 4. Format the response if no box was found
        if not best_box:
            return Response({
                "recommended_box": None,
                "total_order_weight": total_weight,
                "reason": reason,
                "alternative_valid_boxes": []
            })
            
        # 5. Format the successful JSON response
        return Response({
            "recommended_box": {
                "id": best_box.id,
                "name": best_box.name,
                "dimensions": f"{best_box.internal_length} x {best_box.internal_width} x {best_box.internal_height}",
                "cost": str(best_box.cost)
            },
            "total_order_weight": total_weight,
            "reason": reason,
            "alternative_valid_boxes": [
                {
                    "id": b.id,
                    "name": b.name,
                    "dimensions": f"{b.internal_length} x {b.internal_width} x {b.internal_height}",
                    "cost": str(b.cost)
                } for b in other_boxes
            ]
        })