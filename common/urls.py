from django.urls import path

from .views import RegisterView, CustomLoginView, MenuItemListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("Login/", CustomLoginView.as_view(), name="Login"),
    path("menu/", MenuItemListView.as_view(), name="MenuItem"),
]
