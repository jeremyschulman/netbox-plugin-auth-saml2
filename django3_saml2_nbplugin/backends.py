from typing import Optional
from django.contrib.auth.models import User, Group
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings
from saml2.response import AuthnResponse

# Subclass from the Netbox provided RemoteUserBackend so that we get the
# benefits of the REMOTE_AUTH_DEFAULT_GROUPS and
# REMOTE_AUTH_DEFAULT_PERMISSIONS

try:
   from netbox.authentication import RemoteUserBackend
except (ImportError, ModuleNotFoundError):
    from utilities.auth_backends import RemoteUserBackend


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


class SAML2CustomAttrUserBackend(RemoteUserBackend):
    """
    This backend will configure the following attributes from SAML attributes:
        * first_name
        * last_name
        * email
        * any flags
    """

    def authenticate(self, request: WSGIRequest, remote_user: str) -> Optional[User]:
        """
        This method uses a user defined attribute for the username or Name ID if
        USERNAME_ATTR is not configured.
        """
        be_settings = settings.PLUGINS_CONFIG["django3_saml2_nbplugin"].get("CUSTOM_ATTR_BACKEND", {})

        saml2_auth_resp: AuthnResponse = request.META['SAML2_AUTH_RESPONSE']
        user_ident = saml2_auth_resp.get_identity()

        try:
            if "USERNAME_ATTR" in be_settings:
                remote_user = user_ident[be_settings["USERNAME_ATTR"]][0]

        except KeyError as exc:
            missing_attr = exc.args[0]
            be_name = self.__class__.__name__
            raise PermissionError(f"SAML2 backend {be_name} missing attribute: {missing_attr}")

        if be_settings.get("ALWAYS_UPDATE_USER", False):
            user = super().authenticate(request, remote_user)
            # The RemoteUserBackend may return None on auth failure
            if user is None:
                return None
            return self.configure_user(request, user)
        else:
            return super().authenticate(request, remote_user)

    def configure_user(self, request: WSGIRequest, user: User) -> User:
        """
        This method will always be called on login when ALWAYS_UPDATE_USER is True.
        This method will uses SAML attributes to configure the following:
           * first_name
           * last_name
           * email
           * user flags
           * groups
        """
        be_settings = settings.PLUGINS_CONFIG["django3_saml2_nbplugin"].get("CUSTOM_ATTR_BACKEND", {})

        saml2_auth_resp: AuthnResponse = request.META['SAML2_AUTH_RESPONSE']
        user_ident = saml2_auth_resp.get_identity()

        try:
            if "FIRST_NAME_ATTR" in be_settings:
                user.first_name = user_ident[be_settings["FIRST_NAME_ATTR"]][0]
            if "LAST_NAME_ATTR" in be_settings:
                user.last_name = user_ident[be_settings["LAST_NAME_ATTR"]][0]
            if "MAIL_ATTR" in be_settings:
                user.email = user_ident[be_settings["MAIL_ATTR"]][0]
            if "GROUP_ATTR" in be_settings:
                ident_groups = user_ident[be_settings["GROUP_ATTR"]]
            else:
                ident_groups = []
        except KeyError as exc:
            missing_attr = exc.args[0]
            be_name = self.__class__.__name__
            raise PermissionError(f"SAML2 backend {be_name} missing attribute: {missing_attr}")

        if "FLAGS_BY_GROUP" in be_settings and "GROUP_ATTR" in be_settings:
            for flag, group_name in be_settings["FLAGS_BY_GROUP"].items():
                if group_name in ident_groups:
                    setattr(user, flag, True)
                else:
                    setattr(user, flag, False)
        if "GROUP_MAPPINGS" in be_settings and "GROUP_ATTR" in be_settings:
            user_groups = []
            for saml_group, django_group in be_settings["GROUP_MAPPINGS"].items():
                if saml_group in ident_groups:
                    user_groups.append(Group.objects.get(name=django_group))
            user.groups.set(user_groups)
        user.save()

        # call Netbox superclass for further processing of REMOTE_AUTH_xxx variables.
        return super().configure_user(request, user)
