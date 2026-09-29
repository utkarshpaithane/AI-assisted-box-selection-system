from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import Product, Box

class InventoryModelTests(TestCase):
    
    def test_1_product_creation(self):
        """Test 1: Product creation"""
        product = Product.objects.create(name="Book", length=20, width=15, height=5, weight=1.5)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.name, "Book")

    def test_2_box_creation(self):
        """Test 2: Box creation"""
        box = Box.objects.create(name="Small Box", internal_length=25, internal_width=20, internal_height=10, max_weight=5.0, cost="1.50")
        box.refresh_from_db()  # fetch the real Decimal value back from the database
        self.assertEqual(Box.objects.count(), 1)
        self.assertEqual(box.cost, Decimal("1.50"))

    def test_12_invalid_dimensions(self):
        """Test 12: Invalid dimensions (must trigger ValidationError on full_clean)"""
        product = Product(name="Bad Product", length=-5, width=10, height=10, weight=1)
        with self.assertRaises(ValidationError):
            product.full_clean()  # full_clean() runs the model validators

    def test_14_invalid_weight(self):
        """Test 14: Invalid weight"""
        box = Box(name="Bad Box", internal_length=10, internal_width=10, internal_height=10, max_weight=0, cost="1.00")
        with self.assertRaises(ValidationError):
            box.full_clean()