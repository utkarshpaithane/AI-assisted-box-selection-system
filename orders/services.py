import itertools
from typing import Optional, List, Tuple, Set
from inventory.models import Box

class BoxRecommendationService:
    """
    Service for determining the most suitable shipping box for an order.
    
    Assumptions & Limitations:
    - Products are stacked vertically in a single column.
    - Each product is placed on its largest face (largest dim = length, middle = width, smallest = height).
    - Products are not arranged side-by-side.
    - This is a simplified packing strategy, not a full 3D bin-packing algorithm.
    - The algorithm may reject a box that could accommodate the products using a more efficient arrangement.
    - The algorithm is deterministic and easy to explain and test.
    - The unused_space value is a bounding-box-based heuristic, not an exact measurement of physical empty space.
    """

    @staticmethod
    def get_sorted_dimensions(l: float, w: float, h: float) -> Tuple[float, float, float]:
        """Returns dimensions sorted from largest to smallest (Length, Width, Height)."""
        dims = sorted([l, w, h], reverse=True)
        return dims[0], dims[1], dims[2]

    @staticmethod
    def calculate_combined_dimensions(order_items) -> Tuple[float, float, float]:
        """
        Calculates the Combined Bounding Box for the order using the 1D Stacking Method.
        Returns: (required_length, required_width, required_height)
        """
        max_length = 0.0
        max_width = 0.0
        total_height = 0.0

        for item in order_items:
            product = item.product
            qty = item.quantity
            
            # Largest dimension becomes base length, middle is base width, smallest is stacking height
            pl, pw, ph = BoxRecommendationService.get_sorted_dimensions(
                product.length, product.width, product.height
            )
            
            if pl > max_length:
                max_length = pl
            if pw > max_width:
                max_width = pw
                
            total_height += (ph * qty)

        return (max_length, max_width, total_height)

    @staticmethod
    def calculate_total_weight(order_items) -> float:
        """Calculates the total weight of all items in the order."""
        total_weight = 0.0
        for item in order_items:
            total_weight += (item.product.weight * item.quantity)
        return total_weight

    @staticmethod
    def get_unique_orientations(l: float, w: float, h: float) -> Set[Tuple[float, float, float]]:
        """Generates all unique 3D permutations of the given dimensions."""
        return set(itertools.permutations([l, w, h]))

    @staticmethod
    def dimensions_fit(combined_dims: Tuple[float, float, float], box: Box) -> bool:
        """
        Checks if the Combined Bounding Box fits inside the shipping box.
        Tests all unique orientations of the bounding box.
        """
        req_l, req_w, req_h = combined_dims
        unique_orientations = BoxRecommendationService.get_unique_orientations(req_l, req_w, req_h)
        
        for orientation in unique_orientations:
            o_l, o_w, o_h = orientation
            if (o_l <= box.internal_length and 
                o_w <= box.internal_width and 
                o_h <= box.internal_height):
                return True
                
        return False

    @staticmethod
    def calculate_unused_space(combined_dims: Tuple[float, float, float], box: Box) -> float:
        """
        Calculates unused space based on the Combined Bounding Box volume.
        This is a heuristic for selecting a compact box, not exact physical empty space.
        """
        box_volume = box.internal_length * box.internal_width * box.internal_height
        req_volume = combined_dims[0] * combined_dims[1] * combined_dims[2]
        return box_volume - req_volume

    @staticmethod
    def recommend_box(order_items) -> Tuple[Optional[Box], float, str, List[Box]]:
        """
        Filters boxes based on weight and dimensions, then sorts valid boxes 
        by unused space (ascending) and cost (ascending).
        
        Returns: (Recommended Box, Total Weight, Reason String, List of other valid boxes)
        """
        boxes = Box.objects.all()
        if not boxes.exists():
            return None, 0.0, "No boxes available in the system.", []

        total_weight = BoxRecommendationService.calculate_total_weight(order_items)
        combined_dims = BoxRecommendationService.calculate_combined_dimensions(order_items)

        valid_boxes = []

        for box in boxes:
            # 1. Weight Check
            if total_weight > box.max_weight:
                continue
                
            # 2. Dimension Check
            if not BoxRecommendationService.dimensions_fit(combined_dims, box):
                continue
                
            # Both checks passed
            unused_space = BoxRecommendationService.calculate_unused_space(combined_dims, box)
            
            valid_boxes.append({
                'box': box,
                'unused_space': unused_space,
                'cost': box.cost
            })

        if not valid_boxes:
            return None, total_weight, "Order exceeds dimensions or weight capacity of all available boxes.", []

        # Sort by: 1. unused_space (ascending), 2. cost (ascending)
        valid_boxes.sort(key=lambda x: (x['unused_space'], x['cost']))

        best_match = valid_boxes[0]['box']
        other_valid_boxes = [item['box'] for item in valid_boxes[1:]]

        unused_val = round(valid_boxes[0]['unused_space'], 2)
        reason = (f"Selected box with lowest bounding-box unused space ({unused_val} cubic units) "
                  f"and lowest cost. Total order weight is {round(total_weight, 2)}.")

        return best_match, total_weight, reason, other_valid_boxes