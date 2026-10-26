from rest_framework import status
from rest_framework.response import Response


def api_response(
    status_code=status.HTTP_200_OK,
    message="",
    data=None,
    errors=None,
    is_success=True,
):
    payload = {
        "status": "success" if is_success else "error",
        "message": message,
        "data": data,
        "errors": errors,
    }
    return Response(payload, status=status_code)
