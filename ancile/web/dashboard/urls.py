from django.urls import  path
import ancile.web.dashboard.views as views

urlpatterns = [
    path('', views.dashboard),
    path('policies', views.policies),
    path('providers', views.providers),
    path('apps', views.apps),
    path('permissiongroups', views.get_app_groups),
    path('admin/users', views.admin_users),
    path('admin/tokens', views.admin_tokens),
    path('admin/apps', views.admin_apps),
    path('admin/policies', views.admin_policies),
    path('admin/groups', views.admin_groups),
    path('admin/providers', views.admin_providers),
    path('admin/functions', views.admin_functions)
]
