from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Person

def parse_attributes(META):
    shib_attrs = {}
    error = False
    for header, attr in settings.SHIB_ATTRIBUTE_MAP.items():
        required, name = attr
        values = META.get(header, None)
        value = None
        if values:
            # If multiple attributes releases just care about the 1st one
            try:
                value = values.split(';')[0]
            except:
                value = values

        shib_attrs[name] = value
        if not value or value == '':
            if required:
                error = True
    return shib_attrs, error


def build_shib_url(request, target, entityid=None):
    url_base = 'https://%s' % request.get_host()
    shib_url = "%s%s" % (url_base, getattr(settings, 'SHIB_HANDLER', '/Shibboleth.sso/DS'))
    if not target.startswith('http'):
        target = url_base + target

    url = '%s?target=%s' % (shib_url, target)
    if entityid:
        url += '&entityID=%s' % entityid
    return url

def team_from_user_hunt(user, hunt):
    if(user.is_anonymous()):
        return None
    teams1 = get_object_or_404(Person, user=user)
    teams = teams1.teams.filter(hunt=hunt)
    if(len(teams) > 0):
        return teams[0]
    else:
        return None
