from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import loader, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings

from utils import parse_attributes
from forms import BaseRegisterForm


def render_forbidden(*args, **kwargs):
    return HttpResponseForbidden(loader.render_to_string(*args, **kwargs))


def shib_login(request, RegisterForm=BaseRegisterForm,
                  register_template_name='shib_register.html'):

    attr, error = parse_attributes(request.META)
    
    was_redirected = False
    if "next" in request.GET:
        was_redirected = True
    redirect_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    context = {'shib_attrs': attr,
               'was_redirected': was_redirected}
    if error:
        return render_forbidden('attribute_error.html',
                                  context,
                                  context_instance=RequestContext(request))
    try:
        username = attr[settings.SHIB_USERNAME]
        # TODO this should log a misconfiguration.
    except:
        return render_forbidden('attribute_error.html',
                                  context,
                                  context_instance=RequestContext(request))

    if not attr[settings.SHIB_USERNAME] or attr[settings.SHIB_USERNAME] == '':
        return render_forbidden('attribute_error.html',
                                  context,
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(attr)
    try:
        user = User.objects.get(username=attr[settings.SHIB_USERNAME])
    except User.DoesNotExist:
        form = RegisterForm()
        context = {'form': form,
                   'next': redirect_url,
                   'shib_attrs': attr,
                   'was_redirected': was_redirected}
        return render_to_response(register_template_name,
                                  context,
                                  context_instance=RequestContext(request))
    user.set_unusable_password()
    try:
        user.first_name = attr[settings.SHIB_FIRST_NAME]
        user.last_name = attr[settings.SHIB_LAST_NAME]
        user.email = attr[settings.SHIB_EMAIL]
    except:
        pass
    user.save()
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    if not redirect_url or '//' in redirect_url or ' ' in redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    return HttpResponseRedirect(redirect_url)
