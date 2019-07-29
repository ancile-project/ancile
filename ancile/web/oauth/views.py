from django.shortcuts import render, redirect
from ancile.web.dashboard import models
from django.http import Http404, HttpResponseForbidden
from ancile.web.oauth.utils import get_provider
from django.contrib.auth.decorators import login_required
import requests
import time

@login_required
def callback(request, provider):
    provider_object = get_provider(provider)

    session_state = request.session.get('provider_state')
    callback_state = request.GET.get('state')

    if session_state and callback_state:

        if session_state == callback_state:

            code = request.GET.get("code")

            request_body = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": provider_object.redirect_url(request.scheme + "://" + request.get_host()),
                "client_id": provider_object.client_id,
                "client_secret": provider_object.client_secret
            }

            headers = {
                "Authorization": "basic " + provider_object.basic_auth_header
            }

            response = requests.post(provider_object.access_token_url,
                                        headers=headers,
                                        data=request_body)

            response_json = response.json()


            if response.status_code == 200:
                user = request.user     

                token_object = models.Token(
                    user=user,
                    provider=provider_object,
                    token_type=response_json["token_type"],
                    access_token=response_json["access_token"],
                    refresh_token=response_json.get("refresh_token"),
                    expires_at=(time.time()+response_json["expires_in"]),
                )
                token_object.save()

                scopes_raw = response_json.get("scope")
                scopes = scopes_raw.split() if scopes_raw else []

                for scope in scopes:
                    try:
                        scope_object = models.Scope.objects.get(name=scope,
                                                                provider=provider_object)
                    except models.Scope.DoesNotExist:
                        scope_object = models.Scope(
                            name=scope,
                            provider=provider_object,
                            description=""
                        )
                        scope_object.save()
                    finally:
                        token_object.scopes.add(scope_object)    
                return redirect("/")

            return HttpResponseForbidden("Authorization error.")

    return HttpResponseForbidden("Inconsistent state.")

@login_required
def trigger_auth(request, provider):
        
    provider_object = get_provider(provider)

    scopes = request.GET.get("scopes")

    auth_url, state = provider_object.generate_url(scopes,
                                                    request.scheme + "://" + request.get_host())
    request.session['provider_state'] = state
    return redirect(auth_url)
