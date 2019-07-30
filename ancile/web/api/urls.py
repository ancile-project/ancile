from django.urls import path
import ancile.web.api.views as views

urlpatterns = [
    path('run', views.execute_api),
    path('permissions', views.check_permission_group)
]

