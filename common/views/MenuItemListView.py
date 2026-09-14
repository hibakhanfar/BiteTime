from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from common.responses import api_response
from common.permissions import HasRole
from common.models import MenuItem
from common.serializers.MenuItemSerializer import MenuItemSerializer, MenuItemCreateSerializer


class MenuItemListView(ListCreateAPIView):
    queryset = MenuItem.objects.filter(is_available=True)

    def get_permissions(self):
        if self.request.method == "POST":
            self.allowed_roles = ["CHEF"]
            return [HasRole()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MenuItemCreateSerializer
        return MenuItemSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status_code=200, message="Menu retrieved successfully", data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            status_code=201, message="Menu created successfully", data=serializer.data
        )
