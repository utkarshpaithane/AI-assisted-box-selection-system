# AI Usage Documentation

## 1. AI Tools Used

I used the following AI tools during this assignment:

- ChatGPT
- Google Gemini
- Claude
- Google Antigravity

I used these tools for different parts of the development process. I discussed the assignment and explored possible approaches with the AI tools, and used the ideas from these discussions to decide how to structure and implement the project.

Google Antigravity was used to generate the initial project code based on the requirements and approach I had worked out.

After the initial implementation, I used Claude and ChatGPT mainly for debugging, reviewing the implementation, identifying mistakes, understanding errors, and improving the project.

## 2. Prompts Given

The prompts were focused on:

- Understanding and breaking down the Django assignment requirements.
- Discussing possible approaches for the box selection/recommendation system.
- Planning the Django models, API structure, validation, and recommendation service.
- Asking Google Antigravity to implement the project based on the selected approach.
- Reviewing errors and unexpected behavior after the initial implementation.
- Debugging the recommendation logic, validation, API behavior, and automated tests.
- Reviewing the project before submission, including the README, AI usage documentation, and test output.

The prompts were iterative rather than one single prompt: I first used the AI tools to explore ideas and then used the resulting implementation and test output to identify and fix problems.

## 3. Output Accepted

I accepted and used AI-generated suggestions and code where they matched the assignment requirements and worked correctly.

In particular:

- The initial Django project implementation generated using Google Antigravity was used as the starting point.
- Suggestions about Django/DRF project organization were used.
- The Product, Box, Order, and OrderItem structure was implemented.
- The box recommendation logic was separated into a service.
- Validation and automated tests were included.
- Debugging suggestions from Claude and ChatGPT were used when they helped identify and resolve actual project issues.

The generated code was not treated as automatically correct. It was run, tested, reviewed, and modified during development.

## 4. Output Rejected or Modified

I modified AI-generated output whenever it did not match the actual project requirements or produced incorrect behavior.

The main changes included:

- Correcting the order update behavior so unsupported `PUT`/`PATCH` requests return `405` instead of reaching an unsupported nested update path.
- Handling protected product deletion by returning `409 Conflict` with a clear API message instead of exposing a server error.
- Correcting a box cost test so it refreshes the object from the database and compares the `Decimal` value correctly.
- Adding endpoint-level tests for successful box recommendation, empty orders, and orders for which no box fits.
- Adding regression tests for the order-update and protected-product-deletion fixes.
- Updating documentation so that it describes the actual simplified packing implementation and its limitations.

## 5. Mistakes Made by AI

The initial AI-generated implementation had issues that were found during testing and review.

The main issues identified were:

1. `PUT`/`PATCH` on an order could reach an unsupported nested update path and produce a `500` error. This was changed so those methods return `405 Method Not Allowed`.
2. Deleting a product already referenced by an order could expose Django's `ProtectedError` as a `500`. This was changed to return `409 Conflict` with a clear message.
3. A box cost test compared a string value before refreshing the object from the database. The test was corrected to refresh the object and compare against `Decimal("1.50")`.
4. The recommendation endpoint did not have enough endpoint-level tests. Tests were added for success, empty orders, and no-fitting-box cases.

These issues reinforced that AI-generated code still needs to be executed, tested, and reviewed rather than accepted blindly.

## 6. How the Final Code Was Verified

I verified the project by:

1. Running Django's test suite with:

```bash
python manage.py test
```

2. Confirming that Django reported no system-check issues.
3. Confirming that all 18 automated tests passed on my local environment.
4. Reviewing and debugging the implementation during development.
5. Checking the API and recommendation behavior.
6. Adding regression tests for bugs found during review.
7. Reviewing the final project structure and documentation before submission.

Final verified automated test result:

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

## AI-Assisted Development Note

AI tools were used as development assistants, but the final project was verified by running and testing the code. The debugging and verification process was important because the initial AI-generated implementation contained issues that had to be identified and corrected.
