from django.shortcuts import render, redirect
from ancile.web.dashboard import models
from django.http import Http404, HttpResponseForbidden, HttpResponse
from ancile.web.oauth.utils import get_provider
from django.contrib.auth.decorators import login_required
import requests
import time


@login_required
def callback(request, provider):
    provider_object = get_provider(provider)

    session_state = request.session.get("provider_state")
    callback_state = request.GET.get("state")

    if session_state and callback_state:

        if session_state == callback_state:

            code = request.GET.get("code")

            request_body = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": provider_object.redirect_url(
                    request.scheme + "://" + request.get_host()
                ),
                "client_id": provider_object.client_id,
                "client_secret": provider_object.client_secret,
            }

            response = requests.post(
                provider_object.access_token_url,
                headers=provider_object.request_headers,
                data=request_body,
            )

            response_json = response.json()

            if response.status_code == 200:
                user = request.user

                token_query = models.Token.objects.filter(user=user,
                                                          provider=provider_object)
                if token_query.exists():
                    token = token_query[0]
                    token._update_token(response_json)
                else:
                    models.Token.objects.create_token(
                        user, provider_object, response.json()
                    )

                return HttpResponse("<script>window.close();</script>")

            return HttpResponseForbidden("Authorization error.")

    return HttpResponseForbidden("Inconsistent state.")

@login_required
def trigger_auth(request, provider):

    provider_object = get_provider(provider)

    scopes = request.GET.get("scopes")
    close = request.GET.get("close")

    auth_url, state = provider_object.generate_url(
        scopes, request.scheme + "://" + request.get_host()
    )
    request.session["provider_state"] = state
    return redirect(auth_url)
