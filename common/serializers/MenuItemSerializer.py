from rest_framework import serializers
from common.models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "name", "price", "estimated_prep_minutes", "image", "allergen_tags")


class MenuItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("name", "price", "estimated_prep_minutes", "image", "allergen_tags")
