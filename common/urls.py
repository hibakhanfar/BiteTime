from django.urls import path

from .views import RegisterView, CustomLoginView, MenuItemListView, StaffCreateView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("Login/", CustomLoginView.as_view(), name="Login"),
    path("menu/", MenuItemListView.as_view(), name="MenuItem"),
    path("staffcreate/", StaffCreateView.as_view(), name="StaffCreate"),
]
