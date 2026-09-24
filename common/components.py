from common.models.User import User
from common.models import Order, OrderItem, TableCheckIn
from Services import EmailNotificationService
from django.utils import timezone


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


class OrderService:
    @staticmethod
    def create_order(customer, table_number, items_data):
        order = Order.objects.create(customer=customer, table_number=table_number)

        order_items = []
        for item in items_data:
            menu_item = item["menu_item"]
            order_items.append(
                OrderItem(
                    order=order,
                    menu_item=menu_item,
                    quantity=item["quantity"],
                    unit_price_at_time=menu_item.price,
                    special_instructions=item.get("special_instructions", ""),
                )
            )

        OrderItem.objects.bulk_create(order_items)
        return order

    @staticmethod
    def start_preparation(order: Order):
        max_item_prep_time = max(
            item.menu_item.estimated_prep_minutes for item in order.orderitem_set.all()
        )
        active_orders = Order.objects.filter(status=Order.Status.IN_PREP)

        backlog_minutes = 0
        for active_order in active_orders:
            remaining = (active_order.estimated_ready_at - timezone.now()).total_seconds() / 60
            if remaining > 0:
                backlog_minutes += remaining

        total_prep_minutes = max_item_prep_time + backlog_minutes

        order.status = Order.Status.IN_PREP
        order.prep_started_at = timezone.now()
        order.estimated_ready_at = timezone.now() + timezone.timedelta(minutes=total_prep_minutes)
        order.save()

        email_body = (
            f"Hi {order.customer.username},\n\n"
            f"The kitchen has started preparing your order #{order.id} "
            f"(table {order.table_number}).\n"
            f"Estimated ready time: {order.estimated_ready_at:%Y-%m-%d %H:%M}.\n\n"
            f"- BiteTime"
        )
        email_data = {
            "email_subject": f"Your BiteTime order #{order.id} is now being prepared",
            "email_body": email_body,
            "to_email": order.customer.email,
        }
        EmailNotificationService.send_email(email_data)

        return order

    @staticmethod
    def mark_ready(order: Order) -> Order:
        order.status = Order.Status.READY
        order.save()

        email_body = (
            f"Hi {order.customer.username},\n\n"
            f"Your order #{order.id} (table {order.table_number}) is now ready!\n\n"
            f"- BiteTime"
        )
        email_data = {
            "email_subject": f"Your BiteTime order #{order.id} is ready!",
            "email_body": email_body,
            "to_email": order.customer.email,
        }
        EmailNotificationService.send_email(email_data)

        return order
