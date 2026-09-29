from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import ProtectedError
from .models import Product, Box
from .serializers import ProductSerializer, BoxSerializer

# ModelViewSet automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"error": "Cannot delete this product because it is part of an existing order."},
                status=status.HTTP_409_CONFLICT,
            )

class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer