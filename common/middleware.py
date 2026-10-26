import time
import logging

logger = logging.getLogger("audit")


class AuditLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        response = self.get_response(request)

        duration_ms = (time.monotonic() - start_time) * 1000

        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else "anonymous"
        )

        logger.info(
            "%s %s | user=%s | status=%s | duration=%.2fms",
            request.method,
            request.path,
            user,
            response.status_code,
            duration_ms,
        )

        return response
