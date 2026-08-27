from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)

        login_url = reverse("dashboard:login")
        return redirect(f"{login_url}?next={request.path}")

    return wrapper
