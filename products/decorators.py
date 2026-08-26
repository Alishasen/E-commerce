from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.is_superuser or request.user.groups.filter(name="Admin").exists():
            return view_func(request, *args, **kwargs)

        raise PermissionDenied

    return wrapper