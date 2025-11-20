# config/middleware.py
import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("api")


class APILoggingMiddleware(MiddlewareMixin):
    """
    모든 요청/응답을 한 줄로 로깅하는 미들웨어

    예시:
    user=1 ip=127.0.0.1 method=GET path=/api/docs/ status=200 duration=12.34ms
    """

    def process_request(self, request):
        # 요청 시작 시간 기록
        request._start_time = time.perf_counter()

    def process_response(self, request, response):
        try:
            # 처리 시간 계산(ms)
            duration = None
            if hasattr(request, "_start_time"):
                duration = (time.perf_counter() - request._start_time) * 1000
                duration = round(duration, 2)

            # user
            user = getattr(request, "user", None)
            if getattr(user, "is_authenticated", False):
                user_repr = str(user.pk)
            else:
                user_repr = "anonymous"

            # IP
            xff = request.META.get("HTTP_X_FORWARDED_FOR")
            if xff:
                ip = xff.split(",")[0].strip()
            else:
                ip = request.META.get("REMOTE_ADDR")

            method = getattr(request, "method", "-")
            path = getattr(request, "path", "-")
            status = getattr(response, "status_code", "-")

            msg = (
                f"user={user_repr} "
                f"ip={ip} "
                f"method={method} "
                f"path={path} "
                f"status={status}"
            )
            if duration is not None:
                msg += f" duration={duration}ms"

            logger.info(msg)
        except Exception:
            # 로깅 중 에러 나도 서비스 죽지 않게
            logger.exception("APILoggingMiddleware error")

        return response
