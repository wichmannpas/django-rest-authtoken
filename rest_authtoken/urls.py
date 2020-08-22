from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views
from .settings import REGISTRATION_EMAIL_CONFIRM, REGISTRATION_ENABLED

app_name = 'rest_authtoken'

router = SimpleRouter()
router.register('login', views.LoginViewSet, basename='login')

if REGISTRATION_ENABLED:
    router.register('register', views.RegisterViewSet, basename='register')

urlpatterns = router.urls

urlpatterns += [
    path('logout/', views.LogoutView.as_view()),
]

if REGISTRATION_ENABLED and REGISTRATION_EMAIL_CONFIRM:
    urlpatterns += [
        path('register/confirm/<str:token>/', views.confirm_email,
             name='confirm_email'),
    ]
