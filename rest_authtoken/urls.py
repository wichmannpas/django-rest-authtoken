from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views


app_name = 'authtoken'

router = SimpleRouter()
router.register('login', views.LoginViewSet, base_name='login')
router.register('register', views.RegisterViewSet, base_name='register')

urlpatterns = router.urls

urlpatterns += [
    path('logout/', views.LogoutView.as_view()),
]
