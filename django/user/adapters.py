from allauth.account.utils import setup_user_email
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from rest_auth.registration.views import SocialLoginView
from django.conf import settings
from azure.views import AzureOAuth2Adapter
from .models import UserProfile

# This has to stay here to use the proper celery instance with the djcelery_email package
import scheduler.celery # noqa


class DefaultAccountAdapterCustom(DefaultAccountAdapter):
    def validate_unique_email(self, email):  # pragma: no cover
        return email


class AzureLogin(SocialLoginView):
    adapter_class = AzureOAuth2Adapter
    callback_url = settings.SOCIALACCOUNT_CALLBACK_URL
    client_class = OAuth2Client


class MyAzureAccountAdapter(DefaultSocialAccountAdapter):  # pragma: no cover
    def save_user(self, request, sociallogin, form=None):
        u = sociallogin.user
        u.set_unusable_password()
        DefaultAccountAdapterCustom().populate_username(request, u)
        assert not sociallogin.is_existing
        user = sociallogin.user
        name = sociallogin.account.extra_data.get('displayName')

        user_model = get_user_model()
        try:
            old_user = user_model.objects.filter(email=user.email).get()
        except user_model.DoesNotExist:
            user.save()
            sociallogin.account.user = user
            sociallogin.account.save()
            UserProfile.objects.create(user=user, name=name, account_type=UserProfile.DONOR)
            setup_user_email(request, user, sociallogin.email_addresses)
        else:
            sociallogin.account.user = old_user
            sociallogin.account.save()
            sociallogin.user = old_user
            if not old_user.userprofile.name:
                old_user.userprofile.name = name
                old_user.userprofile.save()

        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        return True
