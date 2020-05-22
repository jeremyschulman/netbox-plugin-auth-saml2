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



