from django.urls import path
import ancile.web.api.views as views
from rest_framework.authtoken import views as authviews

urlpatterns = [
    path('run', views.execute_api),
    path('browser_run', views.browser_execute),
    path('parse_policy', views.parse_policy),
    path('app/permissions', views.check_permission_group),
    path('app/add', views.add_predefined_policy_to_user),
    path('app/delete', views.remove_app_for_user),
    path('app/groups', views.get_app_groups),
    path('app/policies', views.get_app_policies),
    path('provider/delete', views.remove_provider_for_user),
    path('provider/scopes', views.get_provider_scopes),
    path('token', authviews.obtain_auth_token)
]
