from rest_framework.views import APIView
from rest_framework import status
from common.permissions import HasRole
from rest_framework.permissions import IsAuthenticated
from common.serializers.OrderSerializer import OrderCreateSerializer, OrderResponseSerializer
from common.responses import api_response
from rest_framework.generics import get_object_or_404
from common.models import Order
from common.components import OrderService
from django.utils import timezone


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


class OrderQueueView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["WAITER"]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status != Order.Status.PLACED:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Cannot queue order with status '{order.status}'. Order must be PLACED first.",
            )

        order.status = Order.Status.QUEUED
        order.save()

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Order queued successfully",
            data={"id": order.id, "status": order.status},
        )


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == "CUSTOMER":
            orders = Order.objects.filter(customer=user)
        else:
            orders = Order.objects.all()

        serializer = OrderResponseSerializer(orders, many=True)

        return api_response(
            status_code=200,
            message="Orders retrieved successfully",
            data=serializer.data,
        )


class OrderStartPrepView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CHEF"]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status != Order.Status.QUEUED:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Cannot in_prep order with status '{order.status}'. Order must be QUEUED first.",
            )

        order = OrderService.start_preparation(order)

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Order is now in preparation",
            data={
                "id": order.id,
                "status": order.status,
                "estimated_ready_at": order.estimated_ready_at,
            },
        )


class OrderMarkReadyView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CHEF"]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status != Order.Status.IN_PREP:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Cannot mark ready order with status '{order.status}'. Order must be IN_PREP first.",
            )

        order = OrderService.mark_ready(order)

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Order is now ready",
            data={"id": order.id, "status": order.status},
        )


class OrderServedView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["WAITER"]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status != Order.Status.READY:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Cannot serve order with status '{order.status}'. Order must be READY first.",
            )

        order.status = Order.Status.SERVED
        order.completed_at = timezone.now()
        order.save()

        return api_response(
            status_code=status.HTTP_200_OK,
            message="Order served successfully",
            data={"id": order.id, "status": order.status, "completed_at": order.completed_at},
        )
