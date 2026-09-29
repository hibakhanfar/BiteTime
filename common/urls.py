from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
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
    OrderStartPrepView,
    OrderMarkReadyView,
    OrderServedView,
    TableCheckInView,
    TableCheckOutView,
    MediaPresignedURLView,
    CustomTokenRefreshView,
    MediaPresignedDownloadView,
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
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    path("users/me/avatar/", UserAvatarUpdateView.as_view(), name="user-avatar-update"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
    path("orders/<int:pk>/queue/", OrderQueueView.as_view(), name="order-queue"),
    path("orders/list/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/start-prep/", OrderStartPrepView.as_view(), name="order-start-prep"),
    path("orders/<int:pk>/mark-ready/", OrderMarkReadyView.as_view(), name="order-mark-ready"),
    path("orders/<int:pk>/served/", OrderServedView.as_view(), name="order-served"),
    path("tables/check-in/", TableCheckInView.as_view(), name="table-check-in"),
    path("tables/check-out/", TableCheckOutView.as_view(), name="table-check-out"),
    path("media/presigned-url/", MediaPresignedURLView.as_view(), name="media-presigned-url"),
    path(
        "media/download-url/",
        MediaPresignedDownloadView.as_view(),
        name="media-download-url",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
