from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .email_confirmation import send_confirmation_email
from .settings import REGISTRATION_EMAIL_CONFIRM


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'password',
        ]
        if REGISTRATION_EMAIL_CONFIRM:
            fields += [
                'email',
            ]
            extra_kwargs = {
                'email': {
                    'required': True,
                },
            }

    def validate_password(self, value):
        if len(value) < 6:
            raise ValidationError('password too short')
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')

        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.save()

        try:
            send_confirmation_email(instance)
        except SMTPException:
            raise ValidationError('failed to send confirmation email')

        return instance
