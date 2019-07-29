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
    path('admin/functions', views.admin_functions),
    path('admin/delete/user/<int:user_id>', views.admin_delete_user),
    path('admin/view/user/<int:user_id>', views.admin_view_user),
    path('admin/delete/token/<int:token_id>', views.admin_delete_token),
    path('admin/view/token/<int:token_id>', views.admin_view_token),
    path('admin/delete/policy/<int:policy_id>', views.admin_delete_policy),
    path('admin/view/policy/<int:policy_id>', views.admin_view_policy)
]
