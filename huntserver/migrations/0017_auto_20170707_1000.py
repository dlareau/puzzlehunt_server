# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import User
from huntserver.models import Person


def printUser(user):
    print("Username: %s, Name: %s %s, Email: %s") % (user.username,
        user.first_name, user.last_name, user.email)


def fix_accounts(apps, schema_editor):
    print("")
    users = User.objects.all()
    for user in users:
        person = Person.objects.get(user=user)
        if("@" in user.username):
            if("@andrew.cmu.edu" in user.username or "@pitt.edu" in user.username):
                if(user.has_usable_password()):
                    if(person.is_shib_acct):
                        # shib is on, acct is shib usernamed, just set unusable pass
                        print("Following user has shib on and the account has " +
                            "a shib related email, but the password is usable. " +
                            "Setting user's password to unusable.")
                        printUser(user)
                        user.set_unusable_password()
                        user.save()
                        print("Changed user password to unusable.")

                    else:
                        # Normal unfortunate user, prompt for more
                        print("Following user has all the signs of being a " +
                            "normal user, but has an email used for shib. " +
                            "Please contact this user and arrange a solution " +
                            "as this is not allowed in the new system.")
                        printUser(user)
                        print("")
                else:
                    if(not person.is_shib_acct):
                        # misconfigured, set shib to true
                        print("Following user has unusable password and " +
                            "should be a shib account anyway, setting " +
                            "account to shib.")
                        printUser(user)
                        person.is_shib_acct = True
                        person.save()
                        print("User converted to shib.")
            else:
                print("Following user is in violation of the new policy of " +
                    "not having '@' in usernames, please make your own call " +
                    "manually, maybe contact the user:")
                printUser(user)
                print("")
        else:
            if(person.is_shib_acct):
                # For this to have happened, the admin screwed up or you
                # cheated a POST request, no sypathy, setting attrs back
                print("Following user has non-email username, but is listed " +
                    "being a shibboleth account:")
                printUser(user)
                print("Setting their account to non-shibboleth user.\n")
                person.is_shib_acct = False
                person.save()

            if(not user.has_usable_password()):
                # For this to have happened, the admin screwed up or you
                # cheated a POST request, no sypathy, setting attrs back
                print("Following user has non-email username, but unusable password:")
                printUser(user)
                unresolved_user = True
                while(unresolved_user):
                    new_password = input("Please enter a new password " +
                        "for this user or just press enter to leave the " +
                        "password unset (not recommended):\n")
                    if(new_password != ""):
                        confirm_password = input("Please confirm password:\n")
                        if(new_password == confirm_password):
                            user.set_password(new_password)
                            user.save()
                            unresolved_user = False
                            print("Password updated.\n")
                    else:
                        print("User left with unusable password.\n")


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0016_team_playtester'),
    ]

    operations = [
        migrations.RunPython(fix_accounts),
    ]
