from django import template
from django.conf import settings
from django.template import Template, Context
from huntserver.models import Hunt
register = template.Library()


@register.simple_tag(takes_context=True)
def hunt_static(context):
    return settings.MEDIA_URL + "hunt/" + str(context['hunt'].hunt_number) + "/"


@register.simple_tag(takes_context=True)
def site_title(context):
    return settings.SITE_TITLE


@register.simple_tag(takes_context=True)
def contact_email(context):
    return settings.CONTACT_EMAIL


@register.filter()
def render_with_context(value):
    return Template(value).render(Context({'curr_hunt': Hunt.objects.get(is_current_hunt=True)}))


@register.simple_tag()
def hints_open(team, puzzle):
    if(team is None or puzzle is None):
        return False
    return team.hints_open_for_puzzle(puzzle)


@register.simple_tag(takes_context=True)
def shib_login_url(context, entityID, next_path):
    if(context['request'].is_secure()):
        protocol = "https://"
    else:
        protocol = "http://"
    shib_str = "https://" + settings.SHIB_DOMAIN + "/Shibboleth.sso/Login"
    entity_str = "entityID=" + entityID
    target_str = "target=" + protocol + context['request'].get_host() + "/shib/login"
    next_str = "next=" + next_path

    return shib_str + "?" + entity_str + "&" + target_str + "?" + next_str
