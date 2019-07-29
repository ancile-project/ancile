from django.urls import  path
import ancile.web.dashboard.views as views

urlpatterns = [
    path('dashboard', views.dashboard),
    path('dashboard/policies', views.policies),
    path('dashboard/providers', views.providers),
    path('dashboard/apps', views.apps),
    path('dashboard/admin/users', views.admin_users),
    path('dashboard/admin/tokens', views.admin_tokens),
    path('dashboard/admin/apps', views.admin_apps),
    path('dashboard/admin/policies', views.admin_policies),
    path('dashboard/admin/groups', views.admin_groups),
    path('dashboard/admin/providers', views.admin_providers),
    path('dashboard/admin/functions', views.admin_functions)
]
