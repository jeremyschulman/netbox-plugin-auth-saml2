# Netbox Plugin for SSO using SAML2

Netbox 2.8 provides enhancements to support remote user authentication uses specific
variables defined in the configuration.py file, as described here:

https://netbox.readthedocs.io/en/stable/configuration/optional-settings/

This repository provides a Netbox plugin that can be used to integrate with a SAML SSO system,
such as Okta.

## System Requirements

You will need to install the [django3-okta-saml2](https://github.com/jeremyschulman/django3-okta-saml2)
into your Netbox environment.

## Netbox Configuration

In the `configuration.py` you will need to enable and configure these
`REMOTE_AUTH_xxx` options at a minimum:

```python
REMOTE_AUTH_ENABLED = True
REMOTE_AUTH_BACKEND = 'utilities.auth_backends.RemoteUserBackend'
REMOTE_AUTH_AUTO_CREATE_USER = True
````

You can also create the other options REMOTE_AUTH_DEFAULT_GROUPS and
REMOTE_AUTH_DEFAULT_PERMISSIONS as described in the online docs.

Next you will need to configure this plugin, provding your specific
configuraiton values as described in
[django3-okta-saml2](https://github.com/jeremyschulman/django3-okta-saml2)
repo.

```python
PLUGINS = ['django3_saml2_nbplugin']

PLUGINS_CONFIG = {
    'django3_saml2_nbplugin': {

        # Use the Netbox default remote backend
        'AUTHENTICATION_BACKEND': REMOTE_AUTH_BACKEND,

        # Metadata is required, choose either remote url or local file path
        'METADATA_LOCAL_FILE_PATH': '/etc/oktapreview-netbox-metadata.xml',

        # Setting based on Okta app settings for the Netbox chicklet
        'NAME_ID_FORMAT': "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
    }
}
```

# Setup New URLs

Unfortunately there is no way to dynamically change the
ROOT_URLCONF.urlpatterns for Netbox; and this is by design.  The only way is to
make a copy of the existing netbox/urls.py file and add the following changes
at the bottom of the file.  You can change (2) the "SSO" URL to be different
based on your Okta app configuration.

```python
# -----------------------------------------------------------------------------
# Added to support Okta SSO SAML 2
#
#    1) import django3_okta_saml2 views
#    2) added 'sso/' URL
#    3) added 'login/' to use SSO route rather than default
# -----------------------------------------------------------------------------

import django3_okta_saml2.views

# Prepend BASE_PATH
urlpatterns = [
    path('sso/', include('django3_okta_saml2.urls')),
    path('login/', django3_okta_saml2.views.signin, name='login'),
    path('{}'.format(settings.BASE_PATH), include(_patterns))
]
```

