import logging
from django.contrib.auth.models import User
from utilities.auth_backends import RemoteUserBackend


class SAML2DottedEmailUserBackend(RemoteUserBackend):
    """
    By default the User name is going to be set to the email adddress by the
    django3_auth_saml2 package.  That said, we want to configure the User
    first name, last name, and email fields as well; but only if the username
    follows the form "firstname.lastname@company.com"
    """

    def configure_user(self, request, user: User):
        logger = logging.getLogger('netbox.authentication.RemoteUserBackend')
        logger.debug(f"SAML2 configure user: {user.username}")

        user.email = user.username
        name, *_ = user.username.partition('@')

        if name.count('.') == 1:
            user.first_name, user.last_name = map(str.title, name.split('.'))
            user.save()

        return super().configure_user(request, user)
