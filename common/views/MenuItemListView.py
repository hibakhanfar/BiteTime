from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from common.responses import api_response
from common.models import MenuItem
from common.serializers.MenuItemSerializer import MenuItemSerializer


class MenuItemListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.filter(is_available=True)
    serializer_class = MenuItemSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return api_response(
            status_code=200,
            message="Menu retrieved successfully",
            data=serializer.data,
        )
