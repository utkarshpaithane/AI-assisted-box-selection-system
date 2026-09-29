from django.test import TestCase
from rest_framework.test import APIClient
from inventory.models import Product, Box
from .models import Order, OrderItem
from .services import BoxRecommendationService

class BoxSelectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_a = Product.objects.create(name="Standard Book", length=20, width=15, height=5, weight=1.0)
        self.product_b = Product.objects.create(name="Large Poster", length=50, width=5, height=5, weight=0.5)

    def test_3_order_creation_api(self):
        """Test 3: Order creation via API"""
        response = self.client.post('/api/orders/', {
            "items": [{"product_id": self.product_a.id, "quantity": 1}]
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)

    def test_4_product_fits_exactly(self):
        """Test 4: Product fits exactly inside box"""
        exact_box = Box.objects.create(name="Exact Box", internal_length=20, internal_width=15, internal_height=5, max_weight=5.0, cost="1.00")
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)
        
        box, _, _, _ = BoxRecommendationService.recommend_box(order.items.all())
        self.assertEqual(box, exact_box)

    def test_5_product_does_not_fit(self):
        """Test 5: Product does not fit (dimensions too small)"""
        tiny_box = Box.objects.create(name="Tiny Box", internal_length=10, internal_width=10, internal_height=10, max_weight=5.0, cost="0.50")
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)
        
        box, _, _, _ = BoxRecommendationService.recommend_box(order.items.all())
        self.assertIsNone(box)

    def test_6_product_fits_after_rotation(self):
        """Test 6: Product fits after rotation"""
        # Box is 5x15x20, product is 20x15x5
        rotated_box = Box.objects.create(name="Rotated Box", internal_length=5, internal_width=15, internal_height=20, max_weight=5.0, cost="1.00")
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)
        
        box, _, _, _ = BoxRecommendationService.recommend_box(order.items.all())
        self.assertEqual(box, rotated_box)

    def test_7_product_exceeds_weight(self):
        """Test 7: Product exceeds box weight capacity"""
        weak_box = Box.objects.create(name="Weak Box", internal_length=30, internal_width=30, internal_height=30, max_weight=0.5, cost="1.00")
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1) # Weighs 1.0
        
        box, _, _, _ = BoxRecommendationService.recommend_box(order.items.all())
        self.assertIsNone(box)

    def test_8_and_9_multiple_products_and_quantities(self):
        """Test 8 & 9: Multiple products & Multiple quantities"""
        big_box = Box.objects.create(name="Big Box", internal_length=55, internal_width=40, internal_height=30, max_weight=20.0, cost="5.00")
        order = Order.objects.create()
        # Stack height = (5 * 2) + (5 * 3) = 25
        # Max length = 50, Max width = 15
        # Combined bounding box = 50 x 15 x 25. Weight = (1.0*2) + (0.5*3) = 3.5
        OrderItem.objects.create(order=order, product=self.product_a, quantity=2)
        OrderItem.objects.create(order=order, product=self.product_b, quantity=3)
        
        box, weight, _, _ = BoxRecommendationService.recommend_box(order.items.all())
        self.assertEqual(box, big_box)
        self.assertEqual(weight, 3.5)

    def test_10_no_suitable_box_exists(self):
        """Test 10: No suitable box exists in the system"""
        # System has no boxes!
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)
        
        box, _, reason, _ = BoxRecommendationService.recommend_box(order.items.all())
        self.assertIsNone(box)
        self.assertEqual(reason, "No boxes available in the system.")

    def test_11_correct_box_selected_multiple_valid(self):
        """Test 11: Correct box selected when multiple boxes are valid (cheapest / least unused space)"""
        # Box A has 30x20x20 volume = 12000
        box_a = Box.objects.create(name="Box A", internal_length=30, internal_width=20, internal_height=20, max_weight=10.0, cost="2.00")
        # Box B has 40x30x30 volume = 36000
        box_b = Box.objects.create(name="Box B", internal_length=40, internal_width=30, internal_height=30, max_weight=10.0, cost="5.00")
        
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1) # 20x15x5
        
        box, _, _, _ = BoxRecommendationService.recommend_box(order.items.all())
        # Should pick Box A because it has less unused space
        self.assertEqual(box, box_a)

    def test_13_invalid_quantity(self):
        """Test 13: Invalid quantity API check"""
        response = self.client.post('/api/orders/', {
            "items": [{"product_id": self.product_a.id, "quantity": -5}]
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_recommend_box_endpoint_success(self):
        """Test API Endpoint: Success case"""
        Box.objects.create(name="Perfect Box", internal_length=30, internal_width=20, internal_height=10, max_weight=5.0, cost="2.00")
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)

        response = self.client.post(f'/api/orders/{order.id}/recommend-box/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recommended_box']['name'], "Perfect Box")

    def test_recommend_box_endpoint_empty_order(self):
        """Test API Endpoint: Empty order handling"""
        order = Order.objects.create()  # Has no items

        response = self.client.post(f'/api/orders/{order.id}/recommend-box/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], "This order has no items.")

    def test_recommend_box_endpoint_no_fit(self):
        """Test API Endpoint: boxes exist but none is big enough"""
        Box.objects.create(name="Tiny Box", internal_length=10, internal_width=10, internal_height=10, max_weight=5.0, cost="0.50")
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)

        response = self.client.post(f'/api/orders/{order.id}/recommend-box/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['recommended_box'])
        self.assertEqual(response.data['alternative_valid_boxes'], [])

    def test_order_update_not_allowed(self):
        """PUT on an order must return 405, not crash with a 500"""
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)
        response = self.client.put(f'/api/orders/{order.id}/', {
            "items": [{"product_id": self.product_a.id, "quantity": 3}]
        }, format='json')
        self.assertEqual(response.status_code, 405)

    def test_delete_product_in_use_returns_409(self):
        """Deleting a product that belongs to an order must return 409, not a 500"""
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1)
        response = self.client.delete(f'/api/products/{self.product_a.id}/')
        self.assertEqual(response.status_code, 409)