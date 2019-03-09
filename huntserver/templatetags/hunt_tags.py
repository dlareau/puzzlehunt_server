from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def hunt_static(context):
    from django.conf import settings
    return settings.MEDIA_URL + "hunt/" + str(context['hunt'].hunt_number) + "/"
