from django import template
register = template.Library()


@register.simple_tag(takes_context=True)
def hunt_static(context):
    from django.conf import settings
    return settings.MEDIA_URL + "hunt/" + str(context['hunt'].hunt_number) + "/"


@register.simple_tag(takes_context=True)
def site_title(context):
    from django.conf import settings
    return settings.SITE_TITLE


@register.simple_tag(takes_context=True)
def shib_login_url(context, entityID, next_path):
    if(context['request'].is_secure()):
        protocol = "https://"
    else:
        protocol = "http://"
    shib_str = "https://puzzlehunt.club.cc.cmu.edu/Shibboleth.sso/Login"
    entity_str = "entityID=" + entityID
    target_str = "target=" + protocol + context['request'].get_host() + "/shib/login"
    next_str = "next=" + next_path

    return shib_str + "?" + entity_str + "&" + target_str + "?" + next_str
