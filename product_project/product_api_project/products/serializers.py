from rest_framework import serializers
from categories.models import Category
from .models import Product

class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    price = serializers.FloatField(required=False, default=0.0)
    category_id = serializers.CharField(max_length=36, required=False, allow_blank=True)
    description = serializers.CharField(allow_blank=True, required=False)

    def validate_category_id(self, value):
        if value and not Category.get_by_id(value):
            raise serializers.ValidationError('Invalid category ID')
        return value

    def create(self, validated_data):
        return Product.create(validated_data)

    def update(self, instance, validated_data):
        Product.update(instance['id'], validated_data)
        return Product.get_by_id(instance['id'])