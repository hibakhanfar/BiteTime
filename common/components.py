from common.models.User import User
from common.models import Order, OrderItem, TableCheckIn, PresignedUpload
from Services import EmailNotificationService, S3Service
from django.utils import timezone
import logging
from django.db import transaction
from django.db.models import Max
from datetime import timedelta

audit_logger = logging.getLogger("audit")


class MediaService:
    ALLOWED_CONTENT_TYPES = {
        "video/mp4",
        "video/quicktime",
        "application/pdf",
    }

    @staticmethod
    def create_presigned_upload_url(user, file_name, content_type):
        result = S3Service.generate_presigned_upload_url(file_name, content_type)

        PresignedUpload.objects.create(
            requested_by=user,
            object_key=result["object_key"],
            original_filename=file_name,
            content_type=content_type,
            expires_at=timezone.now() + timezone.timedelta(seconds=result["expires_in"]),
        )

        return result


class TableService:
    @staticmethod
    def check_in(customer, table_number):
        return TableCheckIn.objects.create(customer=customer, table_number=table_number)

    @staticmethod
    def check_out(customer):
        checkin = TableCheckIn.objects.filter(
            customer=customer, status=TableCheckIn.Status.ACTIVE
        ).first()

        if checkin is None:
            return None

        checkin.status = TableCheckIn.Status.CLOSED
        checkin.checked_out_at = timezone.now()
        checkin.save()

        return checkin


class UserService:
    @staticmethod
    def register_user(
        username: str, email: str, password: str, role: str = User.Role.CUSTOMER
    ) -> User:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
        )
        return user


class InvalidOrderTransition(Exception):
    """Order is not in the state required for this action."""


class OrderService:
    @staticmethod
    def _lock(order_id, expected_status):
        order = Order.objects.select_for_update().select_related("customer").get(pk=order_id)
        if order.status != expected_status:
            raise InvalidOrderTransition(
                f"Order is '{order.status}', expected '{expected_status}'."
            )
        return order

    @staticmethod
    def _log_transition(order, old_status, actor):
        audit_logger.info(
            "ORDER_STATUS | order=%s | %s -> %s | actor=%s",
            order.id,
            old_status,
            order.status,
            actor,
        )

    @staticmethod
    def _send_after_commit(email_data):
        transaction.on_commit(lambda: EmailNotificationService.send_email(email_data))

    @staticmethod
    @transaction.atomic
    def create_order(customer, table_number, items_data):
        order = Order.objects.create(customer=customer, table_number=table_number)
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    menu_item=item["menu_item"],
                    quantity=item["quantity"],
                    unit_price_at_time=item["menu_item"].price,
                    special_instructions=item.get("special_instructions", ""),
                )
                for item in items_data
            ]
        )
        audit_logger.info(
            "ORDER_CREATED | order=%s | customer=%s | table=%s",
            order.id,
            customer.id,
            table_number,
        )
        return order

    @staticmethod
    @transaction.atomic
    def queue_order(order_id, actor="system"):
        order = OrderService._lock(order_id, Order.Status.PLACED)
        order.status = Order.Status.QUEUED
        order.save(update_fields=["status"])
        OrderService._log_transition(order, Order.Status.PLACED, actor)
        return order

    @staticmethod
    @transaction.atomic
    def start_preparation(order_id, actor="system"):
        order = OrderService._lock(order_id, Order.Status.QUEUED)

        items = list(order.orderitem_set.select_related("menu_item"))
        if not items:
            raise InvalidOrderTransition("Order has no items.")
        max_item_prep = max(i.menu_item.estimated_prep_minutes for i in items)

        now = timezone.now()

        last_eta = Order.objects.filter(
            status=Order.Status.IN_PREP, estimated_ready_at__gt=now
        ).aggregate(latest=Max("estimated_ready_at"))["latest"]
        start_at = max(now, last_eta) if last_eta else now

        order.status = Order.Status.IN_PREP
        order.prep_started_at = now
        order.estimated_ready_at = start_at + timedelta(minutes=max_item_prep)
        order.save(update_fields=["status", "prep_started_at", "estimated_ready_at"])
        OrderService._log_transition(order, Order.Status.QUEUED, actor)

        OrderService._send_after_commit(
            {
                "email_subject": f"Your BiteTime order #{order.id} is now being prepared",
                "email_body": (
                    f"Hi {order.customer.username},\n\n"
                    f"The kitchen has started preparing your order #{order.id} "
                    f"(table {order.table_number}).\n"
                    f"Estimated ready time: {order.estimated_ready_at:%Y-%m-%d %H:%M} UTC.\n\n"
                    f"- BiteTime"
                ),
                "to_email": order.customer.email,
            }
        )
        return order

    @staticmethod
    @transaction.atomic
    def mark_ready(order_id, actor="system"):
        order = OrderService._lock(order_id, Order.Status.IN_PREP)
        order.status = Order.Status.READY
        order.save(update_fields=["status"])
        OrderService._log_transition(order, Order.Status.IN_PREP, actor)

        OrderService._send_after_commit(
            {
                "email_subject": f"Your BiteTime order #{order.id} is ready!",
                "email_body": (
                    f"Hi {order.customer.username},\n\n"
                    f"Your order #{order.id} (table {order.table_number}) is now ready!\n\n"
                    f"- BiteTime"
                ),
                "to_email": order.customer.email,
            }
        )
        return order

    @staticmethod
    @transaction.atomic
    def mark_served(order_id, actor="system"):
        order = OrderService._lock(order_id, Order.Status.READY)
        order.status = Order.Status.SERVED
        order.completed_at = timezone.now()
        order.save(update_fields=["status", "completed_at"])
        OrderService._log_transition(order, Order.Status.READY, actor)
        return order
