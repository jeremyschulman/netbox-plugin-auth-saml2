# Netbox Plugin for SSO using SAML2

Netbox 2.8 provides enhancements to support remote user authentication uses specific
variables defined in the configuration.py file, as described here:

https://netbox.readthedocs.io/en/stable/configuration/optional-settings/

This repository provides a Netbox plugin that can be used to integrate with a SAML SSO system,
such as Okta.  

*NOTE: This approach uses a reverse-proxy URL rewrite so that the standard Netbox Login will redirect
the User to the SSO system.  Please refer to the example [nginx.conf](nginx.conf) file.*

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

        # Metadata is required, choose either remote url or local file path
        'METADATA_LOCAL_FILE_PATH': '/etc/oktapreview-netbox-metadata.xml',
    }
}
```

# New Plugin URLs
This plugin will provide two new URLs to Netbox:

`/plugins/sso/login/`<br/>
This URLs redirects the User login to the SSO system (Okta) for authentication.  This is the URL that needs
to be used in the reverse-proxy redirect, for examlple see [nginx.conf](nginx.conf#L35).
<br/>
`/plugins/sso/acs/`<br/>
This URLs should be configured into your SSO system as the route to use to single-sign-on the User into Netbox
after the User has authenticated with the SSO system. 

# Customizing on Create New User Configuration

If you want to customize the way a User is created, beyond what is provided by the
Netbox REMOTE_AUTH variables, you can create a custom RemoteBackend class.  See
the samples in [backends.py](django3_saml2_nbplugin/backends.py).

