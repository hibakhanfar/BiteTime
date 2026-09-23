from celery import shared_task
from django.utils import timezone
from common.models import Order
from common.components import OrderService


@shared_task
def check_and_update_ready_orders():
    orders = Order.objects.filter(status=Order.Status.IN_PREP)
    updated_count = 0

    for order in orders:
        if order.estimated_ready_at and timezone.now() >= order.estimated_ready_at:
            OrderService.mark_ready(order)
            updated_count += 1

    return f"Checked {orders.count()} orders, updated {updated_count} to READY."
