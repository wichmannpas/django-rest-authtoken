from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .email_confirmation import send_confirmation_email
from .settings import REGISTRATION_EMAIL_CONFIRM, REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD


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

    @staticmethod
    def validate_username(value):
        """
        Make sure that no user with this natural key exists.
        This can be used to make usernames case-insensitive, e.g.,
        disallow the registration of two different usernames which
        are equal but with different case.
        """
        try:
            user = get_user_model().objects.get_by_natural_key(value)
        except get_user_model().DoesNotExist:
            return value
        else:
            raise ValidationError('already exists')

    @staticmethod
    def validate_password(value):
        if len(value) < 6:
            raise ValidationError('password too short')
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')

        instance = self.Meta.model(**validated_data)
        instance.set_password(password)

        if REGISTRATION_EMAIL_CONFIRM:
            setattr(instance, REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD, False)

        instance.save()

        if REGISTRATION_EMAIL_CONFIRM:
            try:
                send_confirmation_email(instance)
            except SMTPException:
                raise ValidationError('failed to send confirmation email')

        return instance
