from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=255)
    length = models.FloatField(validators=[MinValueValidator(0.1)])
    width = models.FloatField(validators=[MinValueValidator(0.1)])
    height = models.FloatField(validators=[MinValueValidator(0.1)])
    weight = models.FloatField(validators=[MinValueValidator(0.1)])

    def __str__(self):
        return self.name


class Box(models.Model):
    name = models.CharField(max_length=255)
    internal_length = models.FloatField(validators=[MinValueValidator(0.1)])
    internal_width = models.FloatField(validators=[MinValueValidator(0.1)])
    internal_height = models.FloatField(validators=[MinValueValidator(0.1)])
    max_weight = models.FloatField(validators=[MinValueValidator(0.1)])
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    def __str__(self):
        return f"{self.name} (${self.cost})"