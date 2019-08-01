from django.urls import  path
import ancile.web.dashboard.views as views

urlpatterns = [
    path('', views.dashboard),
    path('register', views.SignUp.as_view()),
    path('policies', views.policies),
    path('providers', views.providers),
    path('apps', views.apps),
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

    path('admin/delete/provider/<int:provider_id>', views.admin_delete_provider),
    path('admin/view/provider/<int:provider_id>', views.admin_view_provider),
    path('admin/edit/provider/<int:provider_id>', views.admin_edit_provider),
    path('admin/add/provider', views.admin_add_provider),

    path('admin/delete/scope/<int:scope_id>', views.admin_delete_scope),
    path('admin/edit/scope/<int:scope_id>', views.admin_edit_scope),
    path('admin/add/scope/<int:provider_id>', views.admin_add_scope),

    path('admin/delete/group/<int:group_id>', views.admin_delete_group),
    path('admin/view/group/<int:group_id>', views.admin_view_group),
    path('admin/add/group/<int:app_id>', views.admin_add_group),
    path('admin/edit/group/<int:group_id>', views.admin_edit_group),

    path('admin/delete/function/<int:function_id>', views.admin_delete_function),
    path('admin/view/function/<int:function_id>', views.admin_view_function),
    path('admin/add/function/<int:app_id>', views.admin_add_function),
    path('admin/edit/function/<int:function_id>', views.admin_edit_function),

    path('admin/delete/policy/template/<int:policy_id>', views.admin_delete_policy_template),
    path('admin/view/policy/template/<int:policy_id>', views.admin_view_policy_template),
    path('admin/add/policy/template/<int:group_id>', views.admin_add_policy_template),
    path('admin/edit/policy/template/<int:policy_id>', views.admin_edit_policy_template),

    path('dev', views.dev_console),

    path('dev/delete/app/<int:app_id>', views.dev_delete_app),
    path('dev/view/app/<int:app_id>', views.dev_view_app),
    path('dev/add/app', views.dev_add_app),
    path('dev/edit/app/<int:app_id>', views.dev_edit_app),

    path('dev/delete/group/<int:group_id>', views.dev_delete_group),
    path('dev/view/group/<int:group_id>', views.dev_view_group),
    path('dev/add/group/<int:app_id>', views.dev_add_group),
    path('dev/edit/group/<int:group_id>', views.dev_edit_group),

    path('dev/delete/policy/template/<int:policy_id>', views.dev_delete_policy),
    path('dev/view/policy/template/<int:policy_id>', views.dev_view_policy),
    path('dev/add/policy/template/<int:group_id>', views.dev_add_policy),
    path('dev/edit/policy/template/<int:policy_id>', views.dev_edit_policy),
]
