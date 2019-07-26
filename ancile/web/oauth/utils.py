from ancile.web.dashboard.models import DataProvider
from django.http import Http404

def get_provider(provider):
    try:
        provider_object = DataProvider.objects.get(name=provider)
        return provider_object
    except DataProvider.DoesNotExist:
        raise Http404("Provider not found.")

