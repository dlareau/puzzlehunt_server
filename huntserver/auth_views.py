from django.conf import settings
from django.contrib.auth import logout, login, views
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from huntserver.utils import parse_attributes
from huntserver.info_views import index

from .models import Hunt
from .forms import UserForm, PersonForm, ShibUserForm


def login_selection(request):
    """ A mostly static view to render the login selection. Next url parameter is conserved. """

    if 'next' in request.GET:
        context = {'next': request.GET['next']}
    else:
        context = {'next': "/"}

    if(settings.USE_SHIBBOLETH):
        return render(request, "login_selection.html", context)
    else:
        return views.login(request)


def create_account(request):
    """
    A view to create user and person objects from valid user POST data, as well as render
    the account creation form.
    """

    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    teams = curr_hunt.real_teams.all().exclude(team_name="Admin").order_by('pk')
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        pf = PersonForm(request.POST, prefix='person')
        if uf.is_valid() and pf.is_valid():
            user = uf.save()
            user.set_password(user.password)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            person = pf.save(commit=False)
            person.is_shib_acct = False
            person.user = user
            person.save()
            login(request, user)
            return index(request)
        else:
            return render(request, "create_account.html", {'uf': uf, 'pf': pf, 'teams': teams})
    else:
        uf = UserForm(prefix='user')
        pf = PersonForm(prefix='person')
        return render(request, "create_account.html", {'uf': uf, 'pf': pf, 'teams': teams})


def account_logout(request):
    """ A view to logout the user and *hopefully* also logout out the shibboleth system. """

    logout(request)
    if 'next' in request.GET:
        additional_url = request.GET['next']
    else:
        additional_url = ""
    return redirect("/Shibboleth.sso/Logout?return=https://" + request.get_host() + additional_url)


def shib_login(request):
    """
    A view that takes the attributes that the shibboleth server passes back and either logs in
    or creates a new shibboleth user. The view then redirects the user back to where they were.
    """

    # Get attributes from REMOTE_USER/META
    attr, error = parse_attributes(request.META)

    redirect_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    context = {'shib_attrs': attr}
    if error:
        return render(request, 'attribute_error.html', context)

    # Attempt to get username out of attr
    try:
        eppn = attr[settings.SHIB_USERNAME]
    except:
        return render(request, 'attribute_error.html', context)

    # Make sure username exists
    if not attr[settings.SHIB_USERNAME] or attr[settings.SHIB_USERNAME] == '':
        return render(request, 'attribute_error.html', context)

    # For form submission
    if request.method == 'POST':
        uf = ShibUserForm(request.POST)
        pf = PersonForm(request.POST)
        if uf.is_valid() and pf.is_valid():
            user = uf.save()
            user.set_unusable_password()
            user.save()
            person = pf.save(commit=False)
            person.is_shib_acct = True
            person.user = user
            person.save()
        else:
            context = {'user_form': uf, 'person_form': pf, 'next': redirect_url, 'shib_attrs': attr}
            return render(request, "shib_register.html", context)
    # Attempt to look up user in DB, if not found, present the registration form.
    try:
        user = User.objects.get(username=eppn)
    except User.DoesNotExist:
        existing_context = {"username": eppn, "email": eppn}
        try:
            existing_context['first_name'] = attr[settings.SHIB_FIRST_NAME]
            existing_context['last_name'] = attr[settings.SHIB_LAST_NAME]
        except:
            pass
        user_form = ShibUserForm(initial=existing_context)
        person_form = PersonForm()
        context = {'user_form': user_form, 'person_form': person_form, 'next': redirect_url, 'shib_attrs': attr}
        return render(request, "shib_register.html", context)

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)

    # Redirect if nessecary
    if not redirect_url or '//' in redirect_url or ' ' in redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL
    return redirect(redirect_url)
