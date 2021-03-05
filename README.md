# Netbox Plugin for SSO using SAML2

Netbox 2.8 provides enhancements to support remote user authentication uses specific
variables defined in the configuration.py file, as described here:

https://netbox.readthedocs.io/en/stable/configuration/optional-settings/

This repository provides a Netbox plugin that can be used to integrate with a SAML SSO system,
such as Okta.  

*NOTE: This approach uses a reverse-proxy URL rewrite so that the standard Netbox Login will redirect
the User to the SSO system.  Please refer to the example [nginx.conf](nginx.conf) file.*

*NOTE: Netbox plugin for SSO, v2.0+, supports Netbox version 2.9*
*NOTE: Netbox 2.10 is not currently supporting - looking for help!*

## System Requirements

You will need to install the [django3-auth-saml2](https://github.com/jeremyschulman/django3-auth-saml2)
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

        # Custom URL to validate incoming SAML requests against
        'ASSERTION_URL': 'https://netbox.company.com',

        # Populates the Issuer element in authn reques e.g defined as "Audience URI (SP Entity ID)" in SSO
        'ENTITY_ID': 'https://netbox.conpany.com/',

        # Metadata is required, choose either remote url or local file path
        'METADATA_AUTO_CONF_URL': "https://mycorp.okta.com/app/sadjfalkdsflkads/sso/saml/metadata"
    }
}
```

# New Plugin URLs
This plugin will provide two new URLs to Netbox:

`/plugins/sso/login/`<br/>
This URLs redirects the User login to the SSO system (Okta) for authentication.  This is the URL that needs
to be used in the reverse-proxy redirect, for examlple see [nginx.conf](nginx.conf#L35).
<br/><br/>
`/sso/acs/`<br/>
This URLs should be configured into your SSO system as the route to use to single-sign-on/redirection URL the User into Netbox
after the User has authenticated with the SSO system. 

# Customizing on Create New User Configuration
If you want to customize the way a User is created, beyond what is provided by the
Netbox REMOTE_AUTH variables, you can create a custom RemoteBackend class.  See
the samples in [backends.py](django3_saml2_nbplugin/backends.py).

# Using A Reverse Proxy Redirect
The use of this plugin requires a reverse-proxy URL redirect to override the default Netbox `/login/` URL.  There
are two notes in this process:

   1.  You MAY need to disable port in redirect depending on your Netbox installation.  If your Netbox server URL
   does _not_ include a port, then you _must_ disable port redirect.  For example see [nginx.conf](nginx.conf#L19).
   1.  You MUST add the ULR rewrite for the `/login/` URL to use `/plugins/sso/login/`, for example [nginx.conf](nginx.conf#L35).
