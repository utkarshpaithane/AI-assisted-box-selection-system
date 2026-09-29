# AI-Assisted Box Selection System

A Django REST API for recommending a suitable shipping box for an ecommerce order based on product dimensions, quantity, total weight, box dimensions, weight capacity, cost, and a simplified packing strategy.

## Problem

When an ecommerce order is received, the warehouse needs to determine which available shipping box can contain the order.

The system:

1. Stores products and their dimensions/weights.
2. Stores available shipping boxes and their internal dimensions, maximum weight, and cost.
3. Creates orders containing one or more products and quantities.
4. Calculates the total order weight.
5. Calculates a combined bounding box using a simplified 1D stacking approach.
6. Checks available boxes for weight and dimensional constraints.
7. Considers rotations of the resulting combined bounding box.
8. Selects the valid box with the least unused bounding-box space; cost is the secondary criterion.

## Technology Stack

- Python 3
- Django 6.1.1
- Django REST Framework 3.18.1
- SQLite

## Project Structure

```text
box_selection_system/
├── box_selection_system/     # Django project configuration
├── inventory/                # Product and Box models, APIs and tests
├── orders/                   # Order models, APIs, recommendation service and tests
├── manage.py
├── README.md
├── AI_USAGE.md
├── TEST_OUTPUT.md
├── requirements.txt
└── .gitignore
```

### Main components

- `inventory/models.py` - `Product` and `Box` models.
- `inventory/serializers.py` - Product and Box API validation/serialization.
- `inventory/views.py` - Product and Box CRUD API endpoints.
- `inventory/tests.py` - inventory model/API tests.
- `orders/models.py` - `Order` and `OrderItem` models.
- `orders/serializers.py` - Order and order-item validation/serialization.
- `orders/views.py` - Order API and box recommendation endpoint.
- `orders/services.py` - `BoxRecommendationService`, containing the packing/recommendation logic.
- `orders/tests.py` - recommendation and order API tests.

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-assisted-box-selection-system
```

### 2. Create and activate a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Endpoints

The project uses Django REST Framework `ModelViewSet` and a router.

### Products

```text
GET     /api/products/
POST    /api/products/
GET     /api/products/<id>/
PUT     /api/products/<id>/
PATCH   /api/products/<id>/
DELETE  /api/products/<id>/
```

### Boxes

```text
GET     /api/boxes/
POST    /api/boxes/
GET     /api/boxes/<id>/
PUT     /api/boxes/<id>/
PATCH   /api/boxes/<id>/
DELETE  /api/boxes/<id>/
```

### Orders

```text
GET     /api/orders/
POST    /api/orders/
GET     /api/orders/<id>/
DELETE  /api/orders/<id>/
```

Order `PUT` and `PATCH` are intentionally disabled because the current nested `OrderSerializer` supports creation of order items but does not implement nested order updates. The API returns `405 Method Not Allowed` instead of allowing an unsupported update to fail with a server error.

### Recommend a box

```text
POST /api/orders/<id>/recommend-box/
```

Example order creation:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

After creating an order, call:

```text
POST /api/orders/1/recommend-box/
```

The recommendation response contains the recommended box, total order weight, selection reason, and other valid boxes.

## Box Recommendation Approach

The implementation intentionally uses a simplified 1D stacking model rather than a full 3D bin-packing algorithm.

For each product:

- The three dimensions are sorted from largest to smallest.
- The largest dimension is treated as the base length.
- The middle dimension is treated as the base width.
- The smallest dimension is treated as the stacking height.
- Quantities increase the total stacking height.
- Across different products, the maximum base length and maximum base width are used.

This produces a combined bounding box for the order.

The service then:

1. Calculates total order weight.
2. Rejects boxes whose maximum weight is insufficient.
3. Checks whether the combined bounding box fits inside the box.
4. Tests all unique orientations of the combined bounding box.
5. Calculates bounding-box unused space for valid boxes.
6. Sorts valid boxes by unused space ascending and cost ascending.
7. Returns the first box as the recommendation.

### Selection rule

The current implementation prioritizes **least unused bounding-box space first**, with **lower cost as the secondary criterion**.

This means the system does not simply choose the cheapest valid box. A tighter-fitting box can be selected over a cheaper but much roomier valid box.

### Known limitation

This is a simplified packing strategy. Products are treated as a single vertical stack and are not arranged side-by-side. Therefore, an order that could physically fit using a more sophisticated 3D arrangement may be rejected by this implementation.

For example, multiple small cubes can sometimes fit inside a box by arranging them across its length and width, while the simplified vertical-stack calculation may reject the same order because its calculated stack height is too large.

The `unused_space` value is also a bounding-box-based heuristic rather than an exact calculation of physical empty space.

## Validation

The API/model validation covers:

- Positive product dimensions.
- Positive product weight.
- Positive box dimensions.
- Positive maximum box weight.
- Non-negative box cost.
- Positive order-item quantity.
- Orders containing at least one item.

These validations are enforced through the model/serializer validation path; they should not be described as database-level constraints.

## Testing

Run the automated test suite with:

```bash
python manage.py test
```

The current verified test run completed successfully with:

```text
Found 18 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..................
----------------------------------------------------------------------
Ran 18 tests in 0.160s

OK
Destroying test database for alias 'default'...
```

The detailed test output is recorded in `TEST_OUTPUT.md`.

The test suite covers product and box creation/validation, recommendation logic, rotations, weight limits, multiple products and quantities, no-fit cases, API recommendation success/empty/no-fit cases, order update behavior, and protected product deletion.

## AI Usage

AI assistance was used during development. The specific tools, development workflow, accepted/modified output, mistakes found, and verification steps are documented in `AI_USAGE.md`.

## Submission Notes

The repository should not include the local virtual environment (`venv/`), Python cache files, the local SQLite database, or other generated local files.

The assignment also requires the candidate's own exported chat transcript and a personally written response describing what was learned. Those should be added separately according to the assignment instructions.
