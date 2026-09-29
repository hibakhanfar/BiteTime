from rest_framework import serializers
from common.models import MenuItem, TableCheckIn
from common.components import OrderService


class OrderItemCreateSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.filter(is_available=True),
        error_messages={
            "does_not_exist": "This menu item does not exist or is currently unavailable.",
        },
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    special_instructions = serializers.CharField(required=False, allow_blank=True, max_length=500)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True, allow_empty=False)

    def validate(self, attrs):
        customer = self.context["request"].user
        checkin = TableCheckIn.objects.filter(
            customer=customer, status=TableCheckIn.Status.ACTIVE
        ).first()

        if checkin is None:
            raise serializers.ValidationError(
                "You must check in to a table before placing an order."
            )

        attrs["table_number"] = checkin.table_number
        return attrs

    def create(self, validated_data):
        customer = self.context["request"].user
        return OrderService.create_order(
            customer=customer,
            table_number=validated_data["table_number"],
            items_data=validated_data["items"],
        )


class OrderItemResponseSerializer(serializers.Serializer):
    menu_item_name = serializers.CharField(source="menu_item.name")
    quantity = serializers.IntegerField()
    unit_price_at_time = serializers.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = serializers.CharField(required=False, allow_null=True)


class OrderResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    table_number = serializers.IntegerField()
    status = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    placed_at = serializers.DateTimeField()
    prep_started_at = serializers.DateTimeField(allow_null=True)
    estimated_ready_at = serializers.DateTimeField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    items = OrderItemResponseSerializer(source="orderitem_set", many=True)
