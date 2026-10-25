import warnings
from django.core import signing
from django.conf import settings as django_settings

from .exceptions import TokenScopeError

warnings.simplefilter("once")


def get_token(user, action, **kwargs):
    username = user.get_username()
    if hasattr(username, "pk"):
        username = username.pk
    payload = {user.USERNAME_FIELD: username, "action": action}
    if kwargs:
        payload.update(**kwargs)
    token = signing.dumps(payload)
    return token


def get_token_payload(token, action, exp=None):
    payload = signing.loads(token, max_age=exp)
    _action = payload.pop("action")
    if _action != action:
        raise TokenScopeError
    return payload


def get_token_paylod(token, action, exp=None):
    warnings.warn(
        "get_token_paylod is deprecated, use get_token_payload instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_token_payload(token, action, exp)


def using_refresh_tokens():
    if (
        hasattr(django_settings, "GRAPHQL_JWT")
        and django_settings.GRAPHQL_JWT.get("JWT_LONG_RUNNING_REFRESH_TOKEN", False)
        and "graphql_jwt.refresh_token.apps.RefreshTokenConfig"
        in django_settings.INSTALLED_APPS
    ):
        return True
    return False


def revoke_user_refresh_token(user):
    if using_refresh_tokens():
        refresh_tokens = user.refresh_tokens.all()
        for refresh_token in refresh_tokens:
            try:
                refresh_token.revoke()
            except Exception:  # JSONWebTokenError
                pass


def flat_dict(dict_or_list):
    """
    if is dict, return list of dict keys,
    if is list, return the list
    """
    return list(dict_or_list.keys()) if isinstance(dict_or_list, dict) else dict_or_list


def normalize_fields(dict_or_list, extra_list):
    """
    helper merge settings defined fileds and
    other fields on mutations
    """
    if isinstance(dict_or_list, dict):
        for i in extra_list:
            dict_or_list[i] = "String"
        return dict_or_list
    else:
        return dict_or_list + extra_list


def with_late_fields(output, **late_fields):
    """
    Set fields that mixins add to ``_meta.fields`` after the class is created,
    such as ``token`` and ``refresh_token``. graphene 3 builds ``__init__`` from
    the fields a class has when it is created, so they can't be keyword
    arguments, and the ones not given are left unset. graphene 2 set every
    field, so those default to ``None`` here too.
    """
    for name in type(output)._meta.fields:
        if not hasattr(output, name):
            setattr(output, name, None)
    for name, value in late_fields.items():
        setattr(output, name, value)
    return output
