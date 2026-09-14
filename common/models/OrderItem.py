from . import Order, MenuItem
from django.db import models


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_at_time = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)
