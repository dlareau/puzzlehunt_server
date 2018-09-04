from django.test import TestCase
from django.core.urlresolvers import reverse
from huntserver import models, forms
from django.contrib.auth.models import User

#python manage.py dumpdata --indent=4  --exclude=contenttypes --exclude=sessions --exclude=admin --exclude=auth.permission

# Users: jlareau, user1, user2, user3, user4, user5, user6
#   jlareau is superuser/staff and on no teams
#   user1 is on teams 2, 6, 8 (1-2, 2-3, 3-2)
#   user2 is on teams 2, 6, 9 (1-2, 2-3, 3-3)
#   user3 is on teams 3, 5    (1-3, 2-2     )
#   user4 is on teams 3, 4    (1-3, 2-1     )
#   user5 is on teams    6    (     2-3     )
#   user6 is not on any teams

# 3 Hunts: hunt 1 is in the past, hunt 2 is current and running, hunt 3 is in the future
#   Hunt 1: Team limit of 5
#   Hunt 2: Team limit of 3
#   Hunt 3: Team limit of 3

# 3 puzzles per hunt
# 3 teams per hunt, in each hunt, second team is a playtesting team

def login(test, username):
    test.assertTrue(test.client.login(username=username, password='password'))

def get_and_check_page(test, page, code, args={}):
    response = test.client.get(reverse(page, kwargs=args))
    test.assertEqual(response.status_code, code)
    return response

def ajax_and_check_page(test, page, code, args={}):
    response = test.client.get(reverse(page), args, 
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
    test.assertEqual(response.status_code, code)
    return response

def solve_puzzle_from_admin(test):
    test.client.logout()
    login(test, 'user5')
    post_context = {'answer': "wrong answer"}
    response = test.client.post(reverse('huntserver:puzzle', kwargs={"puzzle_id":"201"}), post_context)
    test.assertEqual(response.status_code, 200)
    post_context = {'answer': "ANSWER21"}
    response = test.client.post(reverse('huntserver:puzzle', kwargs={"puzzle_id":"201"}), post_context)
    test.assertEqual(response.status_code, 200)
    post_context = {'answer': "wrong answer"}
    response = test.client.post(reverse('huntserver:puzzle', kwargs={"puzzle_id":"202"}), post_context)
    test.assertEqual(response.status_code, 200)
    response = test.client.post(reverse('huntserver:puzzle', kwargs={"puzzle_id":"201"}), post_context)
    test.assertEqual(response.status_code, 200)
    test.client.logout()
    login(test, 'admin')

class nonWebTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_unicode(self):
        rv = str(models.Hunt.objects.all()[0])
        rv = str(models.Puzzle.objects.all()[0])
        rv = str(models.Person.objects.all()[0])
        rv = str(models.Team.objects.all()[0])

class InfoTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_index(self):
        "Test the index page"
        response = get_and_check_page(self, 'huntserver:index', 200)
        self.assertTrue(isinstance(response.context['curr_hunt'], models.Hunt))

    def test_hunt_info(self):
        "Test the hunt info page"
        response = get_and_check_page(self, 'huntserver:current_hunt_info', 200)
        self.assertTrue(response.context['curr_hunt'])
        self.assertTrue(isinstance(response.context['curr_hunt'], models.Hunt))

    def test_previous_hunts(self):
        "Test the previous hunts page"
        response = get_and_check_page(self, 'huntserver:previous_hunts', 200)
        self.assertTrue('hunts' in response.context)
        for hunt in response.context['hunts']:
            self.assertTrue(isinstance(hunt, models.Hunt))

    def test_registration1(self):
        "Test the registration page when not logged in"
        response = get_and_check_page(self, 'huntserver:registration', 200)
        self.assertEqual(response.context['error'], "")

    def test_registration2(self):
        "Test the registration page when logged in and on a team"
        login(self, 'user1')
        response = get_and_check_page(self, 'huntserver:registration', 200)
        self.assertTrue('registered_team' in response.context)
        self.assertTrue(isinstance(response.context['registered_team'], models.Team))

    def test_registration3(self):
        "Test the registration page when logged in and not on a team"
        login(self, 'user6')
        response = get_and_check_page(self, 'huntserver:registration', 200)
        self.assertEqual(response.context['error'], "")
        self.assertTrue('teams' in response.context)
        for hunt in response.context['teams']:
            self.assertTrue(isinstance(hunt, models.Team))

    def test_registration_post_new(self):
        "Test the registration page's join team functionality"
        login(self, 'user6')
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
        login(self, 'user6')
        post_context = {"form_type":"join_team", "team_name":"Team2-2",
                        "join_code":"JOIN5"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['user'].person.teams.all()), 1)
        team = response.context['user'].person.teams.all()[0]
        self.assertEqual(response.context['registered_team'], team)
        self.assertEqual(team.team_name, post_context['team_name'])
        self.assertEqual(team.hunt, models.Hunt.objects.get(is_current_hunt=True))
        self.assertEqual(len(team.person_set.all()), 2)

    def test_registration_post_leave(self):
        "Test the registration page's leave team functionality"
        login(self, 'user4')
        post_context = {"form_type":"leave_team"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "")
        hunt = models.Hunt.objects.get(is_current_hunt=True)
        self.assertEqual(len(response.context['user'].person.teams.filter(hunt=hunt)), 0)
        self.assertEqual(len(models.Team.objects.get(team_name="Team2-2").person_set.all()), 1)

    def test_registration_post_change_location(self):
        "Test the registration page's leave team functionality"
        login(self, 'user4')
        post_context = {"form_type":"new_location", "team_location": "location2.0"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertEqual(response.status_code, 200)
        hunt = models.Hunt.objects.get(is_current_hunt=True)
        team = response.context['user'].person.teams.filter(hunt=hunt)[0]
        self.assertEqual(response.context['registered_team'], team)
        self.assertEqual(team.location, post_context['team_location'])

    def test_registration_post_invalid_data(self):
        "Test the registration page with invalid post data"
        login(self, 'user6')

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

        post_context = {"form_type":"join_team", "team_name":"Team2-3",
                        "join_code":"JOIN6"}
        response = self.client.post(reverse('huntserver:registration'), post_context)
        self.assertNotEqual(response.context['error'], "")
        self.assertEqual(response.status_code, 200)

    def test_user_profile(self):
        "Test the user profile page"
        login(self, 'user4')
        response = get_and_check_page(self, 'huntserver:user_profile', 200)
        self.assertTrue(isinstance(response.context['user_form'], forms.ShibUserForm))
        self.assertTrue(isinstance(response.context['person_form'], forms.PersonForm))

    def test_user_profile_post_update(self):
        "Test the ability to update information on the user profile page"
        login(self, 'user4')
        user = User.objects.get(username="user4")
        post_context = {'first_name': user.first_name, 'last_name': user.last_name,
                        'username': user.username, 'email': 'test@test.com',
                        'phone': user.person.phone, 'allergies': user.person.allergies}
        response = self.client.post(reverse('huntserver:user_profile'), post_context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].email, "test@test.com")

    def test_user_profile_post_invalid_data(self):
        "Test the profile page with incorrect data"
        login(self, 'user4')
        user = User.objects.get(username="user4")
        post_context = {'first_name': user.first_name, 'last_name': user.last_name,
                        'username': user.username, 'email': 'user3@example.com',
                        'phone': user.person.phone, 'allergies': user.person.allergies}
        response = self.client.post(reverse('huntserver:user_profile'), post_context)
        self.assertEqual(response.status_code, 200)

    def test_resources(self):
        "Test the resources page"
        response = get_and_check_page(self, 'huntserver:resources', 200)

    def test_contact_us(self):
        "Test the contact us page"
        response = get_and_check_page(self, 'huntserver:contact_us', 200)


class HuntTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_protected_static(self):
        "Test the static file protected view"
        login(self, 'user1')
        response = get_and_check_page(self, 'huntserver:protected_static', 200, {"file_path":"/"})
        response = get_and_check_page(self, 'huntserver:protected_static', 200, {"file_path":"puzzles/101/example.pdf"})
        response = get_and_check_page(self, 'huntserver:protected_static', 404, {"file_path":"puzzles/201/example.pdf"})
        
    def test_hunt_normal(self):
        "Test the basic per-hunt view"
        login(self, 'user4')
        response = get_and_check_page(self, 'huntserver:hunt', 200, {"hunt_num":"1"})
        response = get_and_check_page(self, 'huntserver:hunt', 200, {"hunt_num":"2"})
        response = get_and_check_page(self, 'huntserver:hunt', 200, {"hunt_num":"3"})
        self.assertTemplateUsed(response, 'not_released.html')


    def test_current_hunt(self):
        "Test the current hunt redirect"
        login(self, 'user1')
        response = get_and_check_page(self, 'huntserver:current_hunt', 200)

    def test_puzzle_normal(self):
        "Test the basic per-puzzle view"
        login(self, 'user4')
        response = get_and_check_page(self, 'huntserver:puzzle', 200, {"puzzle_id":"101"})
        post_context = {'answer': "Wrong Answer"}
        response = self.client.post(reverse('huntserver:puzzle', 
                                            kwargs={"puzzle_id":"101"}), 
                                    post_context)
        self.assertEqual(response.status_code, 200)
        response = get_and_check_page(self, 'huntserver:puzzle', 200, {"puzzle_id":"201"})
        post_context = {'answer': "Wrong Answer"}
        response = self.client.post(reverse('huntserver:puzzle', 
                                            kwargs={"puzzle_id":"201"}), 
                                    post_context)
        self.assertEqual(response.status_code, 200)
        post_context = {'answer': "ANSWER21"}
        response = self.client.post(reverse('huntserver:puzzle', 
                                            kwargs={"puzzle_id":"201"}), 
                                    post_context)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('huntserver:puzzle', 
                                            kwargs={"puzzle_id":"201"}), 
                                    {'last_date': '2000-01-01T01:01:01.001Z'}, 
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)


    def test_chat_normal(self):
        "Test the basic chat view"
        login(self, 'user1')
        response = get_and_check_page(self, 'huntserver:chat', 200)

    def test_unlockables(self):
        "Test the unlockables view"
        login(self, 'user1')
        response = get_and_check_page(self, 'huntserver:unlockables', 200)        

class AuthTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_create_account(self):
        "Test the account creation view"
        response = get_and_check_page(self, 'huntserver:create_account', 200)
        post_context = {'user-first_name': "first", 'user-last_name': "last", 
                        'user-username': "user7",
                        'user-email': 'user7@example.com', 'person-phone': "777-777-7777", 
                        'person-allergies': "something", 'user-password': "password",
                        'user-confirm_password':"password"}
        post_context['user-email'] = "user6@example.com"
        response = self.client.post(reverse('huntserver:create_account'), post_context)
        self.assertEqual(response.status_code, 200)
        post_context['user-email'] = "user7@example.com"
        post_context['user-username'] = "$$$"
        response = self.client.post(reverse('huntserver:create_account'), post_context)
        self.assertEqual(response.status_code, 200)
        post_context['user-username'] = "user7"
        post_context['user-confirm_password'] = "wordpass"
        response = self.client.post(reverse('huntserver:create_account'), post_context)
        self.assertEqual(response.status_code, 200)
        post_context['user-confirm_password'] = "password"
        response = self.client.post(reverse('huntserver:create_account'), post_context)
        self.assertEqual(response.status_code, 200)

    def test_login_selection(self):
        "Test the login selection view"
        response = get_and_check_page(self, 'huntserver:login_selection', 200)

    def test_account_logout(self):
        "Test the account logout view"
        login(self, 'user1')
        response = get_and_check_page(self, 'huntserver:account_logout', 302)

    def test_shib_login(self):
        "Test the shib login view"
        META = {"Shib-Identity-Provider": 'https://login.cmu.edu/idp/shibboleth',
                "eppn": "jlareau@andrew.cmu.edu", "givenName": "John Dillon",
                "sn": "Lareau"}
        response = self.client.get(reverse('huntserver:new_shib_account'), **META)
        self.assertEqual(response.status_code, 200)

class StaffTests(TestCase):
    fixtures = ["basic_hunt"]

    def test_staff_queue(self):
        "Test the staff queue view"
        login(self, 'admin')
        response = get_and_check_page(self, 'huntserver:queue', 200)
        response = ajax_and_check_page(self, 'huntserver:queue', 200, 
                                       {'last_date': '2000-01-01T01:01:01.001Z'})

    def test_staff_queue_paged(self):
        "Test the staff paged queue view"
        login(self, 'admin')
        response = self.client.get(reverse('huntserver:queue_paged', kwargs={"page_num":"1"}))

    def test_staff_progress(self):
        "Test the staff progress view"
        login(self, 'admin')
        response = get_and_check_page(self, 'huntserver:progress', 200)
        ajax_args = {'last_solve_pk': '0', 'last_submission_pk': '0', 'last_unlock_pk': '0',}
        response = ajax_and_check_page(self, 'huntserver:progress', 200, ajax_args)
        response = ajax_and_check_page(self, 'huntserver:progress', 404, {'last_solve_pk': '1'})
        solve_puzzle_from_admin(self)
        response = ajax_and_check_page(self, 'huntserver:progress', 200, ajax_args)
        response = get_and_check_page(self, 'huntserver:progress', 200)

    def test_staff_charts(self):
        "Test the staff charts view"
        login(self, 'admin')
        response = get_and_check_page(self, 'huntserver:charts', 200)
        solve_puzzle_from_admin(self)
        response = get_and_check_page(self, 'huntserver:charts', 200)

    def test_staff_control(self):
        "Test the staff control view"
        login(self, 'admin')
        post_context = {'action': "initial"}
        response = self.client.post(reverse('huntserver:control'), post_context)
        self.assertEqual(response.status_code, 302)
        post_context = {'action': "reset"}
        response = self.client.post(reverse('huntserver:control'), post_context)
        self.assertEqual(response.status_code, 302)
        post_context = {'action': "getpuzzles"}
        response = self.client.post(reverse('huntserver:control'), post_context)
        self.assertEqual(response.status_code, 302)
        post_context = {'action': "getpuzzles", "puzzle_number":"1"}
        response = self.client.post(reverse('huntserver:control'), post_context)
        self.assertEqual(response.status_code, 302)
        post_context = {'action': "new_current_hunt", "hunt_num":"1"}
        response = self.client.post(reverse('huntserver:control'), post_context)
        self.assertEqual(response.status_code, 302)
        post_context = {'action': "foobar"}
        response = self.client.post(reverse('huntserver:control'), post_context)
        self.assertEqual(response.status_code, 200)

    def test_staff_emails(self):
        "Test the staff email view"
        login(self, 'admin')
        response = get_and_check_page(self, 'huntserver:emails', 200)

    def test_staff_management(self):
        "Test the staff management view"
        login(self, 'admin')
        response = get_and_check_page(self, 'huntserver:hunt_management', 200)

    def test_staff_depgraph(self):
        "Test the staff depgraph view"
        login(self, 'admin')
        response = get_and_check_page(self, 'huntserver:depgraph', 200)

"""
admin.py
Admin interface

auth_views.py
login_selection with 'next' parameter
logging out of an account via the url with a 'next' parameter
bad cases in shib logins

forms.py
shib user trying to change username

hunt_views.py
hunt view as staff
hunt view as playtester
hunt view as not registered
(see if it is possible to reach else case)
(see if "team is none" after sorting puzzles is possible to reach)
puzzle view when ratelimited
puzzle view submission with invalid submissions
puzzle view submission with no team
puzzle view submission with excecption case?
puzzle view ajax with no team
puzzle view ajax with exception case?
puzzle view when public and exception case?
chat view message submission
chat view message submission with invalid data
chat view with no team
chat view ajax
add chat messages to basic_hunt so that we enter the for loop
unlockables view with no team

info_views.py
registration view with team name update

models.py
check if serialize for ajax is still needed/used (if so, use it)
unicode on all models
basically just call a bunch of model functions from everything

staff_views.py
queue post request
queue page exceptions (not possible?)
progress post requests
progress ajax as non-staff (not possible?)
progress normal page with no submissions
all of admin chat
email post request (how to do without emailing?)

bootstrap_tags.py
call the tag with bad data?

utils.py
puzzle submission that matches a response
the rest is errors/edgecases
"""