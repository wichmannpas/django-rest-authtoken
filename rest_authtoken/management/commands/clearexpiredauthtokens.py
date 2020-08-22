from django.core.management import BaseCommand
from rest_authtoken.models import AuthToken, EmailConfirmationToken


class Command(BaseCommand):
    help = 'Delete all epxpired auth and email confirmation tokens'

    def handle(self, *args, **options):
        deleted_auth_tokens = AuthToken.clear_expired_tokens()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully cleared {} auth tokens'.format(deleted_auth_tokens)))
        deleted_email_tokens = EmailConfirmationToken.clear_expired_tokens()
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully cleared {} email confirmation tokens'.format(
                    deleted_email_tokens)))
