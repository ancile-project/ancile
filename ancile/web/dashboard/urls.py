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
    path('admin/edit/user/<int:user_id>', views.admin_edit_user),

    path('admin/delete/token/<int:token_id>', views.admin_delete_token),
    path('admin/view/token/<int:token_id>', views.admin_view_token),

    path('admin/delete/policy/<int:policy_id>', views.admin_delete_policy),
    path('admin/view/policy/<int:policy_id>', views.admin_view_policy),
    path('admin/add/policy/<int:user_id>', views.admin_add_policy),
    path('admin/edit/policy/<int:policy_id>', views.admin_edit_policy),

    path('admin/delete/app/<int:app_id>', views.admin_delete_app),
    path('admin/view/app/<int:app_id>', views.admin_view_app),
    path('admin/edit/app/<int:app_id>', views.admin_edit_app),

    path('admin/delete/group/<int:group_id>', views.admin_delete_group),
    path('admin/view/group/<int:group_id>', views.admin_view_group),
    path('admin/add/group/<int:group_id>', views.admin_add_group),
    path('admin/edit/group/<int:group_id>', views.admin_edit_group)
]
