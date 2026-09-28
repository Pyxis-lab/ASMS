from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("language_switcher.html", takes_context=True)
def language_switcher(context):
    """
    Usage in templates:
        {% load language_switcher %}
        {% language_switcher %}
    """
    request = context.get("request")
    current_lang = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    return {
        "languages": settings.LANGUAGES,
        "current_language": current_lang,
    }