from django3_okta_saml2.config import SAML2_AUTH_CONFIG
from extras.plugins import PluginConfig


class Django3AuthSAML2Plugin(PluginConfig):
    name = 'django3_saml2_nbplugin'
    verbose_name = 'Netbox SSO SAML2 plugin'
    description = 'SSO support using SAML 2.0'
    version = '0.1'
    author = 'Jeremy Schulman'
    base_url = 'sso'

    required_settings = []
    default_settings = {}

    @classmethod
    def validate(cls, user_config):
        super().validate(user_config)
        SAML2_AUTH_CONFIG.update(user_config)


config = Django3AuthSAML2Plugin
