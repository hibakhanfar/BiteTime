from rest_framework.views import APIView
from rest_framework import status
from common.permissions import HasRole
from rest_framework.permissions import IsAuthenticated
from common.serializers.OrderSerializer import OrderCreateSerializer, OrderResponseSerializer
from common.responses import api_response
from rest_framework.generics import get_object_or_404
from common.models import Order
from common.components import OrderService
from common.components import InvalidOrderTransition


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


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == "CUSTOMER":
            orders = Order.objects.filter(customer=user)
        else:
            orders = Order.objects.all()

        orders = orders.prefetch_related("orderitem_set__menu_item")

        serializer = OrderResponseSerializer(orders, many=True)

        return api_response(
            status_code=200,
            message="Orders retrieved successfully",
            data=serializer.data,
        )


def _conflict(exc):
    return api_response(
        status_code=status.HTTP_409_CONFLICT,
        message=str(exc),
    )


class OrderQueueView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["WAITER"]

    def patch(self, request, pk):
        get_object_or_404(Order, pk=pk)  # 404 لو مش موجود
        try:
            order = OrderService.queue_order(pk, actor=request.user.email)
        except InvalidOrderTransition as exc:
            return _conflict(exc)
        return api_response(
            message="Order queued successfully",
            data={"id": order.id, "status": order.status},
        )


class OrderStartPrepView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["CHEF"]

    def patch(self, request, pk):
        get_object_or_404(Order, pk=pk)
        try:
            order = OrderService.start_preparation(pk, actor=request.user.email)
        except InvalidOrderTransition as exc:
            return _conflict(exc)
        return api_response(
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
        get_object_or_404(Order, pk=pk)
        try:
            order = OrderService.mark_ready(pk, actor=request.user.email)
        except InvalidOrderTransition as exc:
            return _conflict(exc)
        return api_response(
            message="Order is now ready",
            data={"id": order.id, "status": order.status},
        )


class OrderServedView(APIView):
    permission_classes = [HasRole]
    allowed_roles = ["WAITER"]

    def patch(self, request, pk):
        get_object_or_404(Order, pk=pk)
        try:
            order = OrderService.mark_served(pk, actor=request.user.email)
        except InvalidOrderTransition as exc:
            return _conflict(exc)
        return api_response(
            message="Order served successfully",
            data={"id": order.id, "status": order.status, "completed_at": order.completed_at},
        )
