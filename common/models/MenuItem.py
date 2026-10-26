from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_prep_minutes = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="menu_items/", null=True, blank=True)
    allergen_tags = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name
