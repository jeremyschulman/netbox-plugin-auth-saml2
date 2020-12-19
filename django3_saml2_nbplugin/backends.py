from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from saml2.response import AuthnResponse

# Subclass from the Netbox provided RemoteUserBackend so that we get the
# benefits of the REMOTE_AUTH_DEFAULT_GROUPS and
# REMOTE_AUTH_DEFAULT_PERMISSIONS

from netbox.authentication import RemoteUserBackend


class SAML2DottedEmailUserBackend(RemoteUserBackend):
    """
    By default the User name is going to be set to the email adddress by the
    django3_auth_saml2 package.  That said, we want to configure the User
    first name, last name, and email fields as well; but only if the username
    follows the form "firstname.lastname@company.com"
    """

    def configure_user(self, request: WSGIRequest, user: User) -> User:
        user.email = user.username
        name, *_ = user.username.partition('@')

        if name.count('.') == 1:
            user.first_name, user.last_name = map(str.title, name.split('.'))
            user.save()

        # call Netbox superclass for further processing of REMOTE_AUTH_xxx variables.
        return super().configure_user(request, user)


class SAML2AttrUserBackend(RemoteUserBackend):
    """
    Do not use email as the User name. Use the SAML2 attributes to configure
    the username, first name, and last name values. This presumes that the
    SAML2 SSO system has been setup to provide the attributes:

        * first_name
        * last_name
        * email

    The User name will be set to <first_name>.<last_name> in lower-case.
    """
    def authenticate(self, request: WSGIRequest, remote_user: str) -> User:
        """
        This method must use the SAML2 attributes to formulate the User name
        the way we want it.
        """
        saml2_auth_resp: AuthnResponse = request.META['SAML2_AUTH_RESPONSE']
        user_ident = saml2_auth_resp.get_identity()

        try:
            first_name = user_ident['first_name'][0].lower()
            last_name = user_ident['last_name'][0].lower()
            remote_user = f"{first_name}.{last_name}"
            return super().authenticate(request, remote_user)

        except KeyError as exc:
            missing_attr = exc.args[0]
            be_name = self.__class__.__name__
            raise PermissionError(f"SAML2 backend {be_name} missing attribute: {missing_attr}")

    def configure_user(self, request: WSGIRequest, user: User) -> User:
        """
        This method is only called when a new User is created.  This method
        will use the SAML2 user identity to configure addition properies about
        the user.  This will include:

           * first_name
           * last_name
           * email
        """

        saml2_auth_resp: AuthnResponse = request.META['SAML2_AUTH_RESPONSE']
        user_ident = saml2_auth_resp.get_identity()

        user.first_name, user.last_name = map(str.title, user.username.split('.'))
        try:
            user.email = user_ident['email'][0]
            user.save()

        except KeyError as exc:
            missing_attr = exc.args[0]
            be_name = self.__class__.__name__
            raise PermissionError(f"SAML2 backend {be_name} missing attribute: {missing_attr}")

        # call Netbox superclass for further processing of REMOTE_AUTH_xxx variables.
        return super().configure_user(request, user)
