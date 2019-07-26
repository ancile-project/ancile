from django.urls import path

from ancile.web.oauth import views

urlpatterns = [
    path("<provider>", views.trigger_auth, name="trigger_auth"),
    path("<provider>/callback", views.callback, name="callback_auth")
]
