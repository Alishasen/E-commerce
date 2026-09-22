from django.shortcuts import redirect

ADMIN_ALLOWED_PREFIXES = (
    "/products/dashboard/",
    "/products/manage/",
    "/admin/",
    "/accounts/",
    "/static/",
    "/media/",
)

class AdminAreaMiddleware:
   
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = getattr(request, "user", None)

        is_admin_account = bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.groups.filter(name="Admin").exists()
            )
        )

        if is_admin_account and not request.path.startswith(
            ADMIN_ALLOWED_PREFIXES
        ):
            return redirect("products:admin_dashboard")

        return self.get_response(request)