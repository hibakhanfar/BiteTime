import logging
import datetime
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger("audit")


class TokenValidityInspector(JWTAuthentication):
    def authenticate(self, request):
        try:
            result = super().authenticate(request)
        except InvalidToken as exc:
            self._log_rejection(request, "invalid_or_expired_token", str(exc))
            raise
        except TokenError as exc:
            self._log_rejection(request, "token_error", str(exc))
            raise AuthenticationFailed("Token is invalid or has expired.")

        if result is None:
            return None

        user, validated_token = result
        self._check_freshness(request, validated_token)

        return user, validated_token

    @staticmethod
    def _check_freshness(request, validated_token):
        issued_at = validated_token.get("iat")

        if issued_at is not None:
            issued_at_dt = timezone.datetime.fromtimestamp(issued_at, tz=datetime.timezone.utc)

            if issued_at_dt > timezone.now():
                TokenValidityInspector._log_rejection(
                    request, "token_issued_in_future", f"iat={issued_at_dt.isoformat()}"
                )
                raise AuthenticationFailed("Token timestamp is invalid.")

    @staticmethod
    def _log_rejection(request, reason, detail):
        logger.info(
            "TOKEN REJECTED | %s %s | reason=%s | detail=%s",
            request.method,
            request.path,
            reason,
            detail,
        )
