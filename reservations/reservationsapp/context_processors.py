from django.conf import settings

def login_redirect_url(request):
    return {'LOGIN_REDIRECT_URL': settings.LOGIN_REDIRECT_URL}
