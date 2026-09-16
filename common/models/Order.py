from django.db import models
from . import User, MenuItem


class Order(models.Model):
    class Status(models.TextChoices):
        PLACED = "PLACED", "Placed"
        QUEUED = "QUEUED", "Queued"
        IN_PREP = "IN_PREP", "In Prep"
        READY = "READY", "Ready"
        SERVED = "SERVED", "Served"

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    table_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)

    placed_at = models.DateTimeField(auto_now_add=True)
    prep_started_at = models.DateTimeField(null=True, blank=True)
    estimated_ready_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    items = models.ManyToManyField(MenuItem, through="OrderItem", related_name="orders")

    @property
    def total_price(self):
        return sum(item.quantity * item.unit_price_at_time for item in self.orderitem_set.all())
