# django-rest-authtoken
A simple token-based authentication backend for Django Rest Framework that stores cryptographically hashed tokens on the server-side. Unlike the upstream auth token implementation of Django Rest Framework, each login generates a new unique token, providing the ability to revoke (or log out) individual sessions rather than all at onces.
Furthermore, only cryptographically hashed values of the tokens are stored on the server, thus a leak of the server-side auth token table does not allow an attacker to use any authenticated sessions.


## Installation

This package can be installed via `pip`:

```bash
pip install django-rest-authtoken
```

To use it, add it to `INSTALLED_APPS` in the Django settings:

```python
INSTALLED_APPS = [
    ...
    'rest_authtoken',
    ...
]
```

 In addition, the package's urls need to be added to the main urlconf:

```python
urlpatterns = [
    ...,
    path('auth/', include('rest_authtoken.urls')),
    ...,
]
```

This will add the URLs `/auth/login/`, `/auth/logout/`, `/auth/register/` (if registration is enabled), and `/auth/register/confirm/<token:str>` (if registration and email confirmation are enabled).

To allow authentication using an `Authorization: Token XXXX` HTTP header, the following configuration is required:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_authtoken.auth.AuthTokenAuthentication',
    ),
}
```

## Usage Examples

### Login

Login:

```bash
curl http://127.0.0.1:8000/auth/login/ --data 'username=john&password=foobar123' -v
...
< HTTP/1.1 200 OK
...
{"token":"As3pLIG8WeltLyZxoRcjQqu7wqPXhzFOMuxqFJjXa-Pb4tIMpzh-Ti21Nah4r38P"}
```

Login (with specified `USER_SERIALIZER`):

```bash
curl http://127.0.0.1:8000/auth/login/ --data 'username=john&password=foobar123' -v
...
< HTTP/1.1 200 OK
...
{"token":"As3pLIG8WeltLyZxoRcjQqu7wqPXhzFOMuxqFJjXa-Pb4tIMpzh-Ti21Nah4r38P","user":{"id":3,"username":"john"}}
```

The supplied token has to be added to all further API requests in the `Authorization` HTTP header.

### Logout

```bash
curl http://127.0.0.1:8000/auth/logout/ -v -H 'Authorization: Token As3pLIG8WeltLyZxoRcjQqu7wqPXhzFOMuxqFJjXa-Pb4tIMpzh-Ti21Nah4r38P' -XDELETE
...
> Authorization: Token g8txWxa2N-u97E-VD2E6SPozZWLLePxeLHu1FsXo3J6HZx1o7ldLkQ-kosk0Vgq6
...
< HTTP/1.1 204 No Content
```

### Registration

Registration (with disabled email confirmation):

```bash
curl http://127.0.0.1:8000/auth/register/ --data 'username=john&password=foobar123' -v
...
< HTTP/1.1 201 Created
...
{"success":true}
```

If the user exists already:

```bash
curl http://127.0.0.1:8000/auth/register/ --data 'username=john&password=foobar123' -v
...
< HTTP/1.1 400 Bad Request
...
{"username":["A user with that username already exists."]}
```

## User Serializer

An optional user serializer can be specified in the settings. If specified, a `user` attribute will be included in successful authentication responses containing the serialized authenticated user. Settings example:

```python
USER_SERIALIZER = 'user.serializers.OwnUserSerializer'
```

## Registration

The registration is disabled by default. To enable it, the following value is required in the Django settings:

```python
REGISTRATION_ENABLED = True
```

## Case-Insensitive Usernames

To make usernames case-insensitive (and thus, prevent the registration of multiple identical usernames with different cases), you could overwrite the `get_by_natural_key` to search for existing usernames case-insensitively:

```python
class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        username_attr = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{username_attr: username})

class User(AbstractUser):
    ...

    objects = CustomUserManager()

    ...
```

`django-rest-authtoken` uses the `get_by_natural_key` method upon registration to verify the uniqueness of the username.

### Confirmation Email

It is possible to optionally enable an email confirmation. An email will be sent upon registration to the provided email address. For this to work, the user model needs to contain a `BooleanField` that stores whether the email address has been confirmed already. If email confirmation should be mandatory to be able to login, this can be set to the `active` field of the user (which is respected by django-rest-authtoken upon login).

A minimal example of a compatible user model could look like this:

```python
class User(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
```

*Warning:* Remember to reset the value of this field to `False` when the email address is changed. This could be achieved by adding the following methods to the user model (keep in mind that this does not catch all cases, for example if using the `QuerySet`'s `update()` method, or when `update_fields` are specified):

```python
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_email = self.email

    def save(self, *args, **kwargs):
        if self.email != self._initial_email:
            self.email_confirmed = False
        super().save(*args, **kwargs)
```

In the Django settings file, the following configuration is required:

```python
REGISTRATION_EMAIL_CONFIRM = True
REGISTRATION_EMAIL_CONFIRM_MODEL_FIELD = 'email_confirmed'
REGISTRATION_EMAIL_CONFIRM_TOKEN_VALIDITY = timedelta(days=1)
REGISTRATION_EMAIL = {
    'BASE_URL': 'https://your-super-service.example.org',  # without trailing slash
    'FROM': 'noreply@example.org',
    'SUBJECT': 'Confirm your email address for FOOBAR',
    'MESSAGE': '''Hello {username},
    please visit the following link to confirm your email address: {url}
    ''',
}
```

The `MESSAGE` attribute is formatted using the Python `format` function, supplying a `username` and a `url` value. The URL is built based on the supplied `BASE_URL` value in the `REGISTRATION_EMAIL` setting.

For internationalization, lazy translation methods (e. g., `gettext_lazy`) can be used. Strings will be translated to the language of the request which causes the email to be sent (if it is triggered by a request).

To send a confirmation email to a user,  `send_confirmation_email(user: get_user_model())` from `rest_authtoken.email_confirmation` can be called with the user object as argument.

Upon successful confirmation, the user is redirected to the path `/`. This can be changed by setting the variable `REGISTRATION_CONFIRM_REDIRECT_PATH` to a different path in the settings.
If the provided token is invalid or expired, the user can be redirected to a path by setting `REGISTRATION_CONFIRM_INVALID_REDIRECT_PATH`. If the value is not specified, a 400 Bad Request is returned with a short and generic (plain-text and unformatted) error message.
**Be careful:** These paths are not checked. You can configure absolute URLs to other domains as well. Make sure not to set this setting to any untrusted value.

#### Manual Confirmation Emails From Django Admin

If you are using the Django admin app, you can define an action for your user model to manually (re)send confirmation emails to users by defining the following action and supplying it to the `ModelAdmin` (make sure to adapt the field names etc. to your own values):

```python
def send_confirmation_emails(modeladmin, request, queryset):
    for user in queryset.filter(email_confirmed=False):
        send_confirmation_email(user)

@admin.register(User)
class OwnUserAdmin(UserAdmin):
    ...
    actions = [send_confirmation_emails]
    ...
```

*Attention:* This action may raise an `smtplib.SMTPException` for any of the supplied users, not sending any confirmation mails to users that would have been processed later.
