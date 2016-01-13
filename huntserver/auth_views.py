from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from huntserver.utils import parse_attributes

from .models import *
from .forms import *

def login_selection(request):
    if 'next' in request.GET:
        context = {'next': request.GET['next']}
    else:
        context = {'next': "/"}
    return render(request, "login_selection.html", context)

def create_account(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    teams = curr_hunt.team_set.all().exclude(team_name="Admin").order_by('pk')
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        pf = PersonForm(request.POST, prefix='person')
        if uf.is_valid() and pf.is_valid():
            user = uf.save()
            user.is_shib_acct = False
            user.save()
            person = pf.save(commit=False)
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
    logout(request)
    if 'next' in request.GET:
        return redirect("/Shibboleth.sso/Logout?return=https://puzzlehunt.club.cc.cmu.edu" + request.GET['next'])
    else:
        return redirect("/Shibboleth.sso/Logout?return=https://puzzlehunt.club.cc.cmu.edu")

def shib_login(request):
  
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
        print(request.POST)
        uf = ShibUserForm(request.POST)
        pf = PersonForm(request.POST)
        print("uf: " + str(uf.is_valid()))
        print("pf: " + str(pf.is_valid()))
        if uf.is_valid() and pf.is_valid():
            user = uf.save()
            user.is_shib_acct = True
            user.set_unusable_password()
            user.save()
            person = pf.save(commit=False)
            person.user = user
            person.save()
        else:
            context = {'user_form': uf, 'person_form': pf, 'next': redirect_url, 'shib_attrs': attr}
            return render(request, "shib_register.html", context)
    # Attempt to look up user in DB, if not found, present the registration form.
    try:
        user = User.objects.get(username=eppn)
    except User.DoesNotExist:
        existing_context = {"username":eppn, "email":eppn}
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