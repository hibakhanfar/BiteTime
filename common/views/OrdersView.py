from rest_framework.views import APIView
from rest_framework import status
from common.permissions import HasRole
from common.serializers.OrderSerializer import OrderCreateSerializer, OrderResponseSerializer
from common.responses import api_response


class OrderCreateView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CUSTOMER"]
    serializer_class = OrderCreateSerializer

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            order = serializer.save()
            response_data = OrderResponseSerializer(order).data
            return api_response(
                status_code=status.HTTP_201_CREATED,
                message="Order placed successfully",
                data=response_data,
            )

        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Order creation failed",
            errors=serializer.errors,
        )
