from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'password',
        )

    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError('the password is too short.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')

        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()
        return instance
