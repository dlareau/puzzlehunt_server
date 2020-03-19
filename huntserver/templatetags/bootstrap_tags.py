from django import template
import logging
register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def active_page(request, view_name):
    from django.urls import resolve, Resolver404
    if not request:
        return ""
    try:
        logger.info(str(resolve(request.path_info)))
        r = resolve(request.path_info)
        url_name_bool = r.url_name == view_name
        if("url" in r.kwargs):
            url_val_bool = view_name.strip("/") in r.kwargs["url"]
        else:
            url_val_bool = False
        return "active" if (url_name_bool or url_val_bool) else ""
    except Resolver404:
        return ""
