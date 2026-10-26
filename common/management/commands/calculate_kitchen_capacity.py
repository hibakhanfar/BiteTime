from django.core.management.base import BaseCommand
from django.utils import timezone
from common.models import Order


class Command(BaseCommand):
    help = "Calculates kitchen bottleneck metrics from active orders (IN_PREP and QUEUED)"

    OVERLOAD_THRESHOLD = 4

    def handle(self, *args, **options):
        in_prep_orders = Order.objects.filter(status=Order.Status.IN_PREP)
        queued_orders = Order.objects.filter(status=Order.Status.QUEUED)

        delays = []
        for order in in_prep_orders:
            if order.estimated_ready_at and timezone.now() > order.estimated_ready_at:
                delay_minutes = (timezone.now() - order.estimated_ready_at).total_seconds() / 60
                delays.append(delay_minutes)

        average_delay = sum(delays) / len(delays) if delays else 0
        is_overloaded = in_prep_orders.count() > self.OVERLOAD_THRESHOLD

        self.stdout.write(self.style.SUCCESS("=== Kitchen Capacity Report ==="))
        self.stdout.write(self.style.SUCCESS(f"Active IN_PREP orders: {in_prep_orders.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Active QUEUED orders: {queued_orders.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Delayed orders: {len(delays)}"))
        self.stdout.write(self.style.SUCCESS(f"Average delay: {average_delay:.2f} minutes"))

        if is_overloaded:
            self.stdout.write(
                self.style.WARNING(
                    f"Kitchen station is OVERLOADED "
                    f"({in_prep_orders.count()} orders IN_PREP, threshold is {self.OVERLOAD_THRESHOLD})"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Kitchen station capacity is normal"))
