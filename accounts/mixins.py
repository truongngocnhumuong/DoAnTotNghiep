from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from accounts.models import User

PERMISSION_DENIED_MESSAGE = "Bạn không có quyền truy cập chức năng này."


def role_required(*roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if getattr(request.user, "role", None) not in roles:
                raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if getattr(request.user, "role", None) not in self.allowed_roles:
            raise PermissionDenied(PERMISSION_DENIED_MESSAGE)
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.ADMIN,)


class HRRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.HR,)


class StaffRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.ADMIN, User.Role.HR)


class CandidateRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.CANDIDATE,)
