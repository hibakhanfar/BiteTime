from django.urls import path

from .views import (
    RegisterView,
    CustomLoginView,
    MenuItemListView,
    UserRoleUpdateView,
    UserListView,
    UserAvatarUpdateView,
    MenuToggleAvailabilityView,
    OrderCreateView,
    OrderQueueView,
    OrderListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("Login/", CustomLoginView.as_view(), name="Login"),
    path("menu/", MenuItemListView.as_view(), name="MenuItem"),
    path("users/<int:pk>/role/", UserRoleUpdateView.as_view(), name="userroleupdate"),
    path("users/", UserListView.as_view(), name="users-list"),
    path(
        "menu/<int:pk>/toggle-availability/",
        MenuToggleAvailabilityView.as_view(),
        name="menu-toggle-availability",
    ),
    path("users/me/avatar/", UserAvatarUpdateView.as_view(), name="user-avatar-update"),
    path("create/orders/", OrderCreateView.as_view(), name="OrderCreate"),
    path("orders/<int:pk>/queue/", OrderQueueView.as_view(), name="order-queue"),
    path("orders/", OrderListView.as_view(), name="order-list"),
]
