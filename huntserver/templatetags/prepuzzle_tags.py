from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def prepuzzle_static(context):
    from django.conf import settings
    return settings.MEDIA_URL + "prepuzzles/" + str(context['puzzle'].pk) + "/"
