from rest_framework import serializers
from categories.models import Category

class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100, required=True, allow_blank=False)
    description = serializers.CharField(allow_blank=True, required=False)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value

    def create(self, validated_data):
        return Category.create(validated_data)

    def update(self, instance, validated_data):
        Category.update(instance['id'], validated_data)
        return Category.get_by_id(instance['id'])