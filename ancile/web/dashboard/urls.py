from django.urls import  path
import ancile.web.dashboard.views as views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.dashboard),
]
