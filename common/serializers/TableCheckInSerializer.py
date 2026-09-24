from rest_framework import serializers
from common.models import TableCheckIn
from common.components import TableService


class TableCheckInCreateSerializer(serializers.Serializer):
    table_number = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        customer = self.context["request"].user

        if TableCheckIn.objects.filter(
            customer=customer, status=TableCheckIn.Status.ACTIVE
        ).exists():
            raise serializers.ValidationError(
                "You already have an active table check-in. Check out first."
            )

        return attrs

    def create(self, validated_data):
        customer = self.context["request"].user
        return TableService.check_in(customer=customer, table_number=validated_data["table_number"])


class TableCheckInResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableCheckIn
        fields = ("id", "table_number", "status", "checked_in_at", "checked_out_at")
