from django.urls import path, include


urlpatterns = [
    path('', include('django3_auth_saml2.urls', namespace='django3_auth_saml2')),
]
