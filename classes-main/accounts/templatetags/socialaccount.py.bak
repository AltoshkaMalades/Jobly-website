from django import template

register = template.Library()


@register.simple_tag
def get_providers():
    """
    Fallback stub for templates that expect `get_providers as ...` when
    `django-allauth` is not installed in the environment (tests/local).
    Returns an empty list of providers so templates render without errors.
    """
    return []


@register.simple_tag
def provider_login_url(provider, process=None):
    """
    Stub for the `provider_login_url` template tag used in templates when
    django-allauth is not available. Returns a safe placeholder URL.
    """
    return '#'
