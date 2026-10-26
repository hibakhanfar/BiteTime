from django.db import models
from . import User


class TableCheckIn(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="check_ins")
    table_number = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    checked_in_at = models.DateTimeField(auto_now_add=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=models.Q(status="ACTIVE"),
                name="unique_active_checkin_per_customer",
            )
        ]

    def __str__(self):
        return f"{self.customer.email} @ table {self.table_number} ({self.status})"
