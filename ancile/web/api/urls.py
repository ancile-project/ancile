from django.urls import path
import ancile.web.api.views as views

urlpatterns = [
    path('run', views.execute_api),
    path('app/permissions', views.check_permission_group),
    path('app/add', views.add_predefined_policy_to_user),
    path('app/delete', views.remove_app_for_user),
    path('app/groups', views.get_app_groups)
]

