# Netbox Plugin for SSO using SAML2

Netbox 2.8 provides enhancements to support remote user authentication uses specific
variables defined in the configuration.py file, as described here:

https://netbox.readthedocs.io/en/stable/configuration/optional-settings/

This repository provides a Netbox plugin that can be used to integrate with a SAML SSO system,
such as Okta.

*NOTE: This approach uses a reverse-proxy URL rewrite so that the standard Netbox Login will redirect
the User to the SSO system.  Please refer to the example [nginx.conf](nginx.conf) file.*

*NOTE: Netbox plugin for SSO, v2.0+, supports Netbox 2.8, 2.9, 2.10, 2.11, 3.0.

## System Requirements

You will need to install the [django3-auth-saml2](https://github.com/jeremyschulman/django3-auth-saml2)
into your Netbox environment.

## Netbox Configuration

In the `configuration.py` you will need to enable and configure these
`REMOTE_AUTH_xxx` options at a minimum:

```python
REMOTE_AUTH_ENABLED = True
REMOTE_AUTH_BACKEND = 'utilities.auth_backends.RemoteUserBackend'
# For v2.8+:
# REMOTE_AUTH_BACKEND = 'netbox.authentication.RemoteUserBackend'
# For backends included with this plugin:
# REMOTE_AUTH_BACKEND = 'django3_saml2_nbplugin.backends.<Backend>'
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

        # Metadata is required, choose either remote url
        'METADATA_AUTO_CONF_URL': "https://mycorp.okta.com/app/sadjfalkdsflkads/sso/saml/metadata",
        # or local file path
        'METADATA_LOCAL_FILE_PATH': '/opt/netbox/saml2.xml',

        # Settings for SAML2CustomAttrUserBackend. Optional.
        'CUSTOM_ATTR_BACKEND': {
            # Attribute containing the username. Optional.
            'USERNAME_ATTR': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
            # Attribute containing the user's email. Optional.
            'MAIL_ATTR': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
            # Attribute containing the user's first name. Optional.
            'FIRST_NAME_ATTR': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
            # Attribute containing the user's last name. Optional.
            'LAST_NAME_ATTR': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
            # Set to True to always update the user on logon
            # from SAML attributes on logon. Defaults to False.
            'ALWAYS_UPDATE_USER': False,
            # Attribute that contains groups. Optional.
            'GROUP_ATTR': 'http://schemas.microsoft.com/ws/2008/06/identity/claims/groups',
            # Dict of user flags to groups.
            # If the user is in the group then the flag will be set to True. Optional.
            'FLAGS_BY_GROUP': {
                'is_staff': 'saml-group1',
                'is_superuser': 'saml-group2'
            },
            # Dict of SAML groups to NetBox groups. Optional.
            # Groups must be created beforehand in NetBox.
            'GROUP_MAPPINGS': {
                'saml-group3': 'netbox-group'
            }
        }
    }
}
```

Please note that `METADATA_AUTO_CONF_URL` and `METADATA_LOCAL_FILE_PATH` are
mutually exclusive. Don't use both settings at the same time.

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

# Adding a SSO Login Button

Instead of using a reverse proxy redirect, you can add a SSO login button above
the NetBox login form. This has the added benefit of allowing both local
and SAML login options.

Add the following to your configuration.py:
```python
BANNER_LOGIN = '<a href="/api/plugins/sso/login" class="btn btn-primary btn-block">Login with SSO</a>'
```

