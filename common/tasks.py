from celery import shared_task
from django.utils import timezone
from common.models import Order
from common.components import OrderService
import logging
from datetime import timedelta

from common.models import PresignedUpload

audit_logger = logging.getLogger("audit")

EXPIRED_RECORD_RETENTION_DAYS = 7


@shared_task
def check_and_update_ready_orders():
    orders = Order.objects.filter(status=Order.Status.IN_PREP)
    updated_count = 0

    for order in orders:
        if order.estimated_ready_at and timezone.now() >= order.estimated_ready_at:
            OrderService.mark_ready(order)
            updated_count += 1

    return f"Checked {orders.count()} orders, updated {updated_count} to READY."


@shared_task
def daily_system_cleanup():
    now = timezone.now()

    archived_count = Order.objects.filter(status=Order.Status.SERVED, is_archived=False).update(
        is_archived=True, archived_at=now
    )

    expired_count = PresignedUpload.objects.filter(
        status=PresignedUpload.Status.PENDING, expires_at__lt=now
    ).update(status=PresignedUpload.Status.EXPIRED)

    cutoff = now - timedelta(days=EXPIRED_RECORD_RETENTION_DAYS)
    deleted_count, _ = PresignedUpload.objects.filter(
        status=PresignedUpload.Status.EXPIRED, expires_at__lt=cutoff
    ).delete()

    summary = (
        f"DAILY CLEANUP | archived_orders={archived_count} "
        f"| expired_links={expired_count} | deleted_links={deleted_count}"
    )
    audit_logger.info(summary)
    return summary
