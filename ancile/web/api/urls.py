from django.urls import path
import ancile.web.api.views as views
from graphene_django.views import GraphQLView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('run', views.execute_api),
    path('parse_policy', views.parse_policy_view),
    path('browser_run', views.browser_execute),
    path('graphene', login_required(GraphQLView.as_view(graphiql=True)))
]
