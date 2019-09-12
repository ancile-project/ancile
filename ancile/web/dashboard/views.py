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

@csrf_protect
@require_http_methods(["POST"])
def signup_view(request):
    data = json.loads(request.body)
    errors = {}
    
    fields = ("username", "password", "firstName", "lastName", "email", )
    
    for field in fields:
        value = data.get(field)
        
        if not value:
            errors[field] = "This field is required"
    
    if not errors.get("username"):
        username = data["username"]
        if User.objects.filter(username=username):
            errors["username"] = "Username already taken"

    if not errors.get("email"):
        email = data["email"]
        if User.objects.filter(email=email):
            errors["email"] = "Another user already registered with this email"
    
    if errors:
        return JsonResponse({"ok": False, "errors": errors})

    user = User(username=username,
                email=email,
                first_name=data['firstName'],
                last_name=data['lastName'])
    user.set_password(data['password'])
    user.save()
    return JsonResponse({"ok": True})
    

def logout_view(request):
    logout(request)
    return render(request, "blank.html")