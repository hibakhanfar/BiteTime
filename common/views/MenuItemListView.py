from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from common.responses import api_response
from common.permissions import HasRole
from common.models import MenuItem
from common.serializers.MenuItemSerializer import MenuItemSerializer, MenuItemCreateSerializer
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status


class MenuItemListView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role in ["MANAGER", "CHEF"]:
            return MenuItem.objects.all()
        return MenuItem.objects.filter(is_available=True)

    def get_permissions(self):
        if self.request.method == "POST":
            self.allowed_roles = ["MANAGER"]
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


class MenuToggleAvailabilityView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CHEF"]

    def patch(self, request, pk):
        menu_item = get_object_or_404(MenuItem, pk=pk)
        menu_item.is_available = not menu_item.is_available
        menu_item.save()

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Availability toggled successfully",
            data={
                "id": menu_item.id,
                "name": menu_item.name,
                "is_available": menu_item.is_available,
            },
        )
