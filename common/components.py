from common.models.User import User
from common.models import Order, OrderItem


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
