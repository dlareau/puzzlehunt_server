import os
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puzzlehunt_server.settings.env_settings")

import django
django.setup()

# your imports, e.g. Django models
from django.contrib.auth.models import User
from huntserver.models import Hunt, Team, Person

from django.core.management import call_command

# Prompt user for confirmation
prompt = ("Are you sure you want to delete all existing database" +
          "data and reset to the loadtest default data?")
prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
while(True):
    ans = input(prompt)
    if not ans:
        sys.exit()
    if ans not in ['y', 'Y', 'n', 'N']:
        print('please enter y or n.')
        continue
    if ans == 'n' or ans == 'N':
        sys.exit()
    if ans == 'y' or ans == 'Y':
        break

# Wipe existing data and load base data
call_command('flush', verbosity=0, interactive=False)
call_command('loaddata', 'locust', ignorenonexistent=True)

# Add in the requested number of users/people/teams
curr_hunt = Hunt.objects.get(is_current_hunt=True)

team_size = curr_hunt.team_size
num_bots = 900  # should be a multiple of 25 and of team size
num_staff = int(num_bots / 25)
num_players = num_bots - num_staff
num_teams = int(num_players / team_size)

print("Now creating %d players, %d teams, and %d staff members" % (num_players, num_teams, num_staff))

for team_index in range(num_teams):
    sys.stdout.write(".")
    team = Team.objects.create(team_name="team_" + str(team_index), hunt=curr_hunt,
                               location="test_loc", join_code="JOIN1")
    for person_index in range(team_size):
        user_number = team_index * team_size + person_index
        user = User.objects.create_user('test_user_' + str(user_number),
                                        'example' + str(user_number) + '@example.com',
                                        'password' + str(user_number))
        person = Person.objects.create(user=user, is_shib_acct=False)
        person.teams.add(team)
        person.save()
for person_index in range(num_staff):
    user_number = person_index + num_players
    user = User.objects.create_superuser('test_user_' + str(user_number),
                                         'example' + str(user_number) + '@example.com',
                                         'password' + str(user_number))
    person = Person.objects.create(user=user, is_shib_acct=False)
    person.save()
print("\n")
