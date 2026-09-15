from django.urls import path

from .views import RegisterView, CustomLoginView, MenuItemListView, UserRoleUpdateView, UserListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("Login/", CustomLoginView.as_view(), name="Login"),
    path("menu/", MenuItemListView.as_view(), name="MenuItem"),
    path("users/<int:pk>/role/", UserRoleUpdateView.as_view(), name="userroleupdate"),
    path("users/", UserListView.as_view(), name="users-list"),
]
