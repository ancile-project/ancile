from django.urls import path
import ancile.web.api.views as views
from graphene_django.views import GraphQLView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('run', views.execute_api),
    path('graphene', login_required(GraphQLView.as_view(graphiql=True)))
]
