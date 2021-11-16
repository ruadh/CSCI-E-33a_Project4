from django.conf import settings

# CITATION:  Passing a settings value to JS from: 
# https://chriskief.com/2013/09/19/access-django-constants-from-settings-py-in-a-template/

def global_settings(request):
    return {
    'CHARACTER_LIMIT': settings.CHARACTER_LIMIT
        }