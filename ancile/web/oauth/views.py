from django.shortcuts import render, redirect
from ancile.web.dashboard import models
from django.http import Http404, HttpResponseForbidden

def callback(request, provider):
    if request.user.is_authenticated:

        session_state = request.session.get('provider_state')
        callback_state = request.GET.get('state')
    
        if session_state and callback_state:

            if session_state == callback_state:

                code = request.GET.get("code")

                # do stuff

        raise HttpResponseForbidden("Inconsistent state.")

    raise HttpResponseForbidden
    
def trigger_auth(request, provider):
    if request.user.is_authenticated:
        
        try:
            provider_object = models.DataProvider.objects.get()
        except DataProvider.DoesNotExist:
            raise Http404("Provider not found.")
        
        auth_url, state = provider_object.generate_url(scopes,
                                                       request.get_host())
        request.session['provider_state'] = state
        return redirect(auth_url, context={'state': state})

    else:
        raise HttpResponseForbidden
