from django.test import TestCase
from django.core.urlresolvers import reverse
from huntserver import models, forms
from django.contrib.auth.models import User

#python manage.py dumpdata --indent=4  --exclude=contenttypes --exclude=sessions --exclude=admin --exclude=auth.permission

class InfoTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_index(self):
        "Test the index page"
        response = self.client.get(reverse('huntserver:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.context['curr_hunt'], models.Hunt))

    def test_hunt_info(self):
        "Test the hunt info page"
        response = self.client.get(reverse('huntserver:current_hunt_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['curr_hunt'])
        self.assertTrue(isinstance(response.context['curr_hunt'], models.Hunt))

    def test_previous_hunts(self):
        "Test the previous hunts page"
        response = self.client.get(reverse('huntserver:previous_hunts'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('hunts' in response.context)
        for hunt in response.context['hunts']:
            self.assertTrue(isinstance(hunt, models.Hunt))

    def test_registration1(self):
        "Test the registration page when not logged in"
        response = self.client.get(reverse('huntserver:registration'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "")

    def test_registration2(self):
        "Test the registration page when logged in and on a team"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('registered_team' in response.context)
        self.assertTrue(isinstance(response.context['registered_team'], models.Team))

    def test_registration3(self):
        "Test the registration page when logged in and not on a team"
        self.assertTrue(self.client.login(username='user6', password='password'))
        response = self.client.get(reverse('huntserver:registration'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "")
        self.assertTrue('teams' in response.context)
        for hunt in response.context['teams']:
            self.assertTrue(isinstance(hunt, models.Team))

    def test_registration_post_new(self):
        "Test the registration page's join team functionality"
        self.assertTrue(self.client.login(username='user6', password='password'))
        post_context = {"form_type":"new_team", "team_name":"new_team",
                        "need_room":"need_a_room"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['user'].person.teams.all()), 1)
        team = response.context['user'].person.teams.all()[0]
        self.assertEqual(response.context['registered_team'], team)
        self.assertEqual(team.team_name, post_context['team_name'])
        self.assertEqual(team.location, post_context['need_room'])
        self.assertEqual(team.hunt, models.Hunt.objects.get(is_current_hunt=True))
        self.assertEqual(team.playtester, False)
        self.assertTrue(len(team.join_code) >= 5)


    def test_registration_post_join(self):
        "Test the registration page's new team functionality"
        self.assertTrue(self.client.login(username='user6', password='password'))
        post_context = {"form_type":"join_team", "team_name":"Team2-2",
                        "join_code":"JOIN5"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['user'].person.teams.all()), 1)
        team = response.context['user'].person.teams.all()[0]
        self.assertEqual(response.context['registered_team'], team)
        self.assertEqual(team.team_name, post_context['team_name'])
        self.assertEqual(team.hunt, models.Hunt.objects.get(is_current_hunt=True))
        self.assertEqual(len(team.person_set.all()), 3)

    def test_registration_post_leave(self):
        "Test the registration page's leave team functionality"
        self.assertTrue(self.client.login(username='user4', password='password'))
        post_context = {"form_type":"leave_team"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "")
        hunt = models.Hunt.objects.get(is_current_hunt=True)
        self.assertEqual(len(response.context['user'].person.teams.filter(hunt=hunt)), 0)
        self.assertEqual(len(models.Team.objects.get(team_name="Team2-2").person_set.all()), 1)

    def test_registration_post_change_location(self):
        "Test the registration page's leave team functionality"
        self.assertTrue(self.client.login(username='user4', password='password'))
        post_context = {"form_type":"new_location", "team_location": "location2.0"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        hunt = models.Hunt.objects.get(is_current_hunt=True)
        team = response.context['user'].person.teams.filter(hunt=hunt)[0]
        self.assertEqual(response.context['registered_team'], team)
        self.assertEqual(team.location, post_context['team_location'])

    def test_registration_post_invalid_data(self):
        "Test the registration page with invalid post data"
        self.assertTrue(self.client.login(username='user6', password='password'))

        post_context = {"form_type":"new_team", "team_name":"team2-2",
                        "need_room":"need_a_room"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertNotEqual(response.context['error'], "")
        self.assertEqual(response.status_code, 200)

        post_context = {"form_type":"new_team", "team_name":"    ",
                        "need_room":"need_a_room"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertNotEqual(response.context['error'], "")
        self.assertEqual(response.status_code, 200)

        post_context = {"form_type":"join_team", "team_name":"Team2-3",
                        "join_code":"JOIN5"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertNotEqual(response.context['error'], "")
        self.assertEqual(response.status_code, 200)

        post_context = {"form_type":"join_team", "team_name":"Team2-2",
                        "join_code":"JOIN0"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertNotEqual(response.context['error'], "")
        self.assertEqual(response.status_code, 200)

    def test_user_profile(self):
        "Test the user profile page"
        self.assertTrue(self.client.login(username='user4', password='password'))
        response = self.client.get(reverse('huntserver:user_profile'))
        self.assertTrue(isinstance(response.context['user_form'], forms.ShibUserForm))
        self.assertTrue(isinstance(response.context['person_form'], forms.PersonForm))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_post_update(self):
        "Test the ability to update information on the user profile page"
        self.assertTrue(self.client.login(username='user4', password='password'))
        user = User.objects.get(username="user4")
        post_context = {'first_name': user.first_name, 'last_name': user.last_name,
                        'username': user.username, 'email': 'test@test.com',
                        'phone': user.person.phone, 'allergies': user.person.allergies}
        response = self.client.post(reverse('huntserver:user_profile'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].email, "test@test.com")

    # TODO: test_user_profile_post_invalid_data

    def test_resources(self):
        "Test the resources page"
        response = self.client.get(reverse('huntserver:resources'))
        self.assertEqual(response.status_code, 200)

    def test_contact_us(self):
        "Test the contact us page"
        response = self.client.get(reverse('huntserver:contact_us'))
        self.assertEqual(response.status_code, 200)


class HuntTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_protected_static(self):
        "Test the static file protected view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:protected_static', args=('/')))
        self.assertEqual(response.status_code, 200)

    def test_hunt_normal(self):
        "Test the basic per-hunt view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:hunt', args=('2',)))
        self.assertEqual(response.status_code, 200)

    def test_current_hunt(self):
        "Test the current hunt redirect"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:current_hunt'))
        self.assertEqual(response.status_code, 200)

    def test_puzzle_normal(self):
        "Test the basic per-puzzle view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:puzzle', args=('201',)))
        self.assertEqual(response.status_code, 200)

    def test_chat_normal(self):
        "Test the basic chat view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:chat'))
        self.assertEqual(response.status_code, 200)

    def test_unlockables(self):
        "Test the unlockables view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)


class AuthTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_create_account(self):
        "Test the account creation view"
        response = self.client.get(reverse('huntserver:create_account'))
        self.assertEqual(response.status_code, 200)

    def test_login_selection(self):
        "Test the login selection view"
        response = self.client.get(reverse('huntserver:login_selection'))
        self.assertEqual(response.status_code, 200)

    # def test_account_logout(self):
    #     "Test the account logout view"
    #     self.assertTrue(self.client.login(username='user1', password='password'))
    #     response = self.client.get(reverse('huntserver:account_logout'))
    #     self.assertEqual(response.status_code, 200)

    # def test_shib_login(self):
    #     "Test the shib login view"
    #     self.assertTrue(self.client.login(username='user1', password='password'))
    #     response = self.client.get(reverse('huntserver:new_shib_account'))
    #     self.assertEqual(response.status_code, 200)

class StaffTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_staff_queue(self):
        "Test the staff queue view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_queue_paged(self):
        "Test the staff paged queue view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_progress(self):
        "Test the staff progress view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_charts(self):
        "Test the staff charts view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_control(self):
        "Test the staff control view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_emails(self):
        "Test the staff email view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_management(self):
        "Test the staff management view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

    def test_staff_depgraph(self):
        "Test the staff depgraph view"
        self.assertTrue(self.client.login(username='user1', password='password'))
        response = self.client.get(reverse('huntserver:unlockables'))
        self.assertEqual(response.status_code, 200)

"""
Test ideas:
- All views
- Test that views with parameters 404 properly upon not getting proper input
- Test access for everything
- update for dev updates

Model list:
Hunts
- (past, present, future)
Puzzles
- (locked, unlocked, solved) in each hunt
Teams
- 3 for each hunt
Persons
- 6 total for various things

Not yet done:
Submissions
- some puzzles with none, some with one, some with many
Solve
Unlock
Messages
Unlockables
Response
Assetfile
"""