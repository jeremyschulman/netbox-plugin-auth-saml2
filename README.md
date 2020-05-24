# Netbox Plugin for SSO using SAML2

Netbox 2.8 provides enhancements to support remote user authentication uses specific
variables defined in the configuration.py file, as described here:

https://netbox.readthedocs.io/en/stable/configuration/optional-settings/

This repository provides a Netbox plugin that can be used to integrate with a SAML SSO system,
such as Okta.  

*Note that the approach in this repo requires you to make a direct modification
to the netbox/urls.py file.  If you want to avoid this small change, you could
try a recommended approach of using a reverse-proxy webserver to perform the
SSO auth rather than directly integrating with Netbox (see notes below for
links.)*

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

You can also create the other options **REMOTE_AUTH_DEFAULT_GROUPS** and
**REMOTE_AUTH_DEFAULT_PERMISSIONS** as described in the online docs.

Next you will need to configure this plugin, provding your specific
configuraiton values as described in
[django3-okta-saml2](https://github.com/jeremyschulman/django3-okta-saml2)
repo, for example:

```python
PLUGINS = ['django3_saml2_nbplugin']

PLUGINS_CONFIG = {
    'django3_saml2_nbplugin': {

        # Use the Netbox default remote backend
        'AUTHENTICATION_BACKEND': REMOTE_AUTH_BACKEND,

        # Metadata is required, choose either remote url or local file path
        'METADATA_LOCAL_FILE_PATH': '/etc/oktapreview-netbox-metadata.xml',
    }
}
```

# Setup New URLs

Unfortunately there is no way to dynamically change the
`ROOT_URLCONF.urlpatterns` for Netbox; and this is by design.  The only way to
integrate this repo is to make a copy of the existing `netbox/urls.py` file and
add the following changes at the bottom of the file.

You can change (2) the "SSO" URL to be different based on your Okta app configuration.

```python
# -----------------------------------------------------------------------------
# Added to support Okta SSO SAML 2
#
#    1) import django3_okta_saml2 views
#    2) added 'sso/' URL for SSO sysytem
#    3) redirect 'login/' to SSO login route rather than default
# -----------------------------------------------------------------------------

import django3_auth_saml2.views

# Prepend BASE_PATH
urlpatterns = [
    path('sso/', include('django3_okta_saml2.urls')),
    path('login/', RedirectView.as_view(url='/sso/login/')),
    path('{}'.format(settings.BASE_PATH), include(_patterns))
]
```

# Customizing on Create New User Configuration

If you want to customize the way a User is created, beyond what is provided by the
Netbox REMOTE_AUTH variables, you can create a custom RemoteBackend class.  See
the samples in [backends.py](django3_saml2_nbplugin/backends.py).

# Using a Reverse-Proxy Approach

A recommended approach is to **NOT** directly integrate SSO into Netbox but
rather perform this functionality using a reverse-proxy that sets the HTTP
header as
[documented](https://netbox.readthedocs.io/en/stable/configuration/optional-settings/).
I have not yet done this, so I cannot qualify if the following links will work;
but it is on my TODO.  Also note that this approach uses OpenID Connect
protocol (OIDC) and not SAML2.

  * [Overview NGINX as an API Gateway for SSO](https://www.okta.com/integrations/nginx-as-api-gateway/)
  * [NXIGX with OIDC](https://github.com/zmartzone/lua-resty-openidc)
  * [Apache with OIDC](https://github.com/zmartzone/mod_auth_openidc)
 
