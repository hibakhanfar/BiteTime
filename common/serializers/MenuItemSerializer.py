from rest_framework import serializers
from common.models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "name", "price", "estimated_prep_minutes", "image", "allergen_tags")


class MenuItemCreateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0.00)
    estimated_prep_minutes = serializers.IntegerField(min_value=1)

    class Meta:
        model = MenuItem
        fields = ("name", "price", "estimated_prep_minutes", "image", "allergen_tags")
