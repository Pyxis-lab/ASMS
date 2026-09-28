"""
Template tag for rendering a language switcher widget.
Drop into any template with: {% load language_switcher %} {% language_switcher %}
"""
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("language_switcher.html")
def language_switcher():
    """Return LANGUAGES for the switcher template."""
    return {"languages": settings.LANGUAGES}