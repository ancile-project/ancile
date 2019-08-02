from django.contrib import admin
from ancile.web.dashboard.models import *

# Register your models here.
admin.site.register(
    [
        User,
        App,
        DataProvider,
        Policy,
        Scope,
        PermissionGroup,
        PolicyTemplate,
        Function,
        Token,
        PrivateData,
    ]
)
