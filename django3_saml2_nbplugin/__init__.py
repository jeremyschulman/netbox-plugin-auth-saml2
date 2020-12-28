"""
This purpose of this plugin is to provide the SAML2_AUTH_CONFIG configuration
to the django3_okta_saml2 package. The .conf module defines SAML2_AUTH_CONFIG
as a dictionary, and this plugin is used to copy the contents provided from the
PLUGIN_CONFIG in configuration.py into SAML2_AUTH_CONFIG.

Do not try to modify django.conf.settings.SAML2_AUTH_CONFIG since by the time
this plugin is invoked the settings is already configured, and if you try
settings.configure(SAML2_AUTH_CONFIG=user_config) an exception will be raised.
"""
from extras.plugins import PluginConfig
from django3_auth_saml2.config import SAML2_AUTH_CONFIG


class Django3AuthSAML2Plugin(PluginConfig):
    name = 'django3_saml2_nbplugin'
    verbose_name = 'Netbox SSO SAML2 plugin'
    description = 'SSO support using SAML 2.0'
    version = '2.0'
    author = 'Jeremy Schulman'
    base_url = 'sso'

    required_settings = []
    default_settings = {}

    @classmethod
    def validate(cls, user_config, *args):
        if len(args) == 1:
            super().validate(user_config, args[0])
        else:
            super().validate(user_config)

        SAML2_AUTH_CONFIG.update(user_config)

config = Django3AuthSAML2Plugin
