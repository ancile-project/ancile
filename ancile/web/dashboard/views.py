from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.contrib.auth import login, logout
import json
from ancile.web.dashboard.models import User
from django.http import JsonResponse

@ensure_csrf_cookie 
def dashboard(request):
    return render(request, "index.html")

@csrf_protect
@require_http_methods(["POST"])
def login_view(request):
    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    if username is not None and password:
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                return JsonResponse({
                    "status": "ok"
                })
        except User.DoesNotExist:
            pass
    
    return JsonResponse({
        "status": "error",
        "error": "Incorrect username or password."
    })

def logout_view(request):
    logout(request)
    return render(request, "blank.html")