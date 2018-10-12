# TEST PLAN
from locust import HttpLocust, TaskSet, TaskSequence, task
import sys
from bs4 import BeautifulSoup

# TODO:
#   Most tests need to be written
#   Implement web browser caching of static files?
#   Maybe add on_start/on_stop arguments to page_and_subpages
#   Fix CSRF to live in the session


# CSRF code:
def CSRF_post(session, response, url, args):
    session.client.headers['Referer'] = session.client.base_url
    csrftoken = response.cookies['csrftoken']
    args['csrfmiddlewaretoken'] = csrftoken
    session.client.post('/accounts/login/', args,
                        headers={"X-CSRFToken": csrftoken},
                        cookies={"csrftoken": csrftoken})


def page_and_subpages(main_function, action_set):
    class ActionSet(TaskSet):
        tasks = action_set

    class ts(TaskSequence):
        tasks = [main_function, ActionSet, stop]

    return ts


def add_static(session, response):
    # Fetches all static resources from a response
    resource_urls = set()
    soup = BeautifulSoup(response.text, "html.parser")

    for res in soup.find_all(src=True):
        url = res['src']
        if ("/static" in url or "/media" in url):
            resource_urls.add(url)

    for res in soup.find_all(href=True):
        url = res['href']
        if ("/static" in url or "/media" in url):
            resource_urls.add(url)

    for url in set(resource_urls):
        if "/media" in url:
            session.client.get(url, name="Media File")
        else:
            session.client.get(url, name="Static File")

    return response


def ensure_login(session, input_response, static=True):
    # Login if login is required and not already logged in
    # optional static arg determines if it should fetch login page static files

    if("login-selection" in input_response.url):
        if("?next=" in input_response.url):
            next_param = input_response.url.split("?next=")[1]
            response = session.client.get("/accounts/login/?next=" + next_param)
            next_url = '/accounts/login/?next=' + next_param
        else:
            response = session, session.client.get("/accounts/login/")
            next_url = '/accounts/login/'

        if(static):
            add_static(session, input_response)
            add_static(session, response)

        session.client.headers['Referer'] = session.client.base_url
        csrftoken = response.cookies['csrftoken']
        args = {"username": "",
                "password": "",
                "csrfmiddlewaretoken": csrftoken
                }

        response = session.client.post(next_url, args,
                                       headers={"X-CSRFToken": csrftoken},
                                       cookies={"csrftoken": csrftoken})
        return response
    else:
        return input_response
    pass


def url_all(l, r):
    add_static(l, ensure_login(l, r))


def stop(l):
    l.interrupt()


# All of the page view functions
def index(l):
    # Load index page
    response = url_all(l, l.client.get("/"))


def current_hunt_main_page(l):
    # Load page, get puzzles, set puzzles on locust object
    # Possibly separate by solved and unsolved
    sys.stdout.write("current hunt main page")


def puzzle_main_page(l):
    # Pick puzzle from puzzles, go to page, possibly weight by solved/unsolved
    # Store current puzzle number in locust object
    # Get ajax number from page and store to locust object
    sys.stdout.write("individual puzzle main page")


def puzzle_ajax(l):
    # make request to current puzzle object with current ajax number
    # store returned ajax number in locust object
    sys.stdout.write("puzzle ajax request")


def puzzle_pdf_link(l):
    # Load pdf link for current puzzle number
    sys.stdout.write("puzzle pdf request")


def puzzle_answer(l):
    # Submit answer to current puzzle using POST with some correctness chance
    sys.stdout.write("submit answer request")


def chat_main_page(l):
    # Load main chat page and store ajax value in locust object
    sys.stdout.write("chat main page")


def chat_ajax(l):
    # Make ajax request with current ajax value and store new value
    sys.stdout.write("chat ajax request")


def chat_new_message(l):
    # Make POST request to create a new chat message, store ajax value
    sys.stdout.write("chat new message request")


def info_main_page(l):
    # Load info page
    response = url_all(l, l.client.get("/hunt/info"))


def registration_main_page(l):
    # Load registration page
    sys.stdout.write("registration main page")


def registration_update_info(l):
    # Update the teams room location
    sys.stdout.write("update team info request")


def resources(l):
    # Load resources page
    response = url_all(l, l.client.get("/resources"))


def previous_hunts_main_page(l):
    # Load previous hunts page, store list of available hunts in locust object
    sys.stdout.write("previous hunts main page")


def previous_hunt(l):
    # Load a random previous hunt page in the locust object
    sys.stdout.write("previous hunt page")


def create_account(l):
    # Load the create account page
    sys.stdout.write("create account page")


def contact(l):
    # Load contact page
    response = url_all(l, l.client.get("/contact"))


def user_profile(l):
    # Load user profile page
    sys.stdout.write("user profile page")


def staff_chat_main_page(l):
    # Load staff chat page, get and store ajax token
    sys.stdout.write("chat main page")


def staff_chat_new_message(l):
    sys.stdout.write("chat message page")


def staff_chat_ajax(l):
    sys.stdout.write("chat ajax request")


def progress_main_page(l):
    sys.stdout.write("progress main page")


def progress_unlock(l):
    sys.stdout.write("progress unlock request")


def progress_ajax(l):
    sys.stdout.write("progress ajax")


def queue_main_page(l):
    sys.stdout.write("queue main page")


def queue_num_page(l):
    sys.stdout.write("queue numbered page")


def queue_new_response(l):
    sys.stdout.write("new response request")


def queue_ajax(l):
    sys.stdout.write("queue ajax")


def email_main_page(l):
    sys.stdout.write("email main page")


def email_send_email(l):
    sys.stdout.write("send email request")


def admin_page(self):
    sys.stdout.write("generic admin page")


def management(self):
    sys.stdout.write("management main page")


# All of the probability stuff
staff_chat_fs = {staff_chat_new_message: 3, staff_chat_ajax: 80, stop: 1}
progress_fs = {progress_unlock: 1, progress_ajax: 150, stop: 4}
queue_fs = {queue_num_page: 1, queue_new_response: 6, queue_ajax: 1000, stop: 3}
email_fs = {email_send_email: 1, stop: 2}

puzzle_fs = {puzzle_ajax: 3000, puzzle_pdf_link: 1, puzzle_answer: 8, stop: 8}
chat_fs = {chat_ajax: 40, chat_new_message: 4, stop: 1}
current_hunt_fs = {page_and_subpages(puzzle_main_page, puzzle_fs): 4,
                   page_and_subpages(chat_main_page, chat_fs): 1,
                   stop: 7}
registration_fs = {registration_update_info: 1, stop: 10}
prev_hunt_fs = {previous_hunt: 3, stop: 1}


class StaffSet(TaskSet):
    tasks = {
        page_and_subpages(staff_chat_main_page, staff_chat_fs): 6,
        page_and_subpages(progress_main_page, progress_fs): 7,
        page_and_subpages(queue_main_page, queue_fs): 8,
        page_and_subpages(email_main_page, email_fs): 2,
        admin_page: 1,
        management: 2
    }


class WebsiteSet(TaskSet):
    tasks = {
        page_and_subpages(current_hunt_main_page, current_hunt_fs): 780,
        info_main_page: 27,
        page_and_subpages(registration_main_page, registration_fs): 20,
        resources: 9,
        page_and_subpages(previous_hunts_main_page, prev_hunt_fs): 6,
        create_account: 1,
        contact: 1,
        user_profile: 1,
        stop: 100
    }


class HunterSet(TaskSequence):
    tasks = [index, WebsiteSet]


# Staff user
class StaffLocust(HttpLocust):
    task_set = StaffSet
    min_wait = 2500
    max_wait = 3000
    weight = 10


# Regular user
class HunterLocust(HttpLocust):
    task_set = HunterSet
    min_wait = 2500
    max_wait = 3000
    weight = 240


# - LOGIN
#   - LOGIN SELECTION
#       - SHIB 14
#       - LOCAL 3

# - STAFF 10
#   - CHAT
#       - AJAX (LOG)
#       - NEW MESSAGE
#   - PROGRESS
#       - AJAX (LOG)
#       - MANUALLY UNLOCK
#   - QUEUE 160
#       - AJAX (LOG)
#       - NUMBERED PAGE 6
#       - SEND NEW RESPONSE 36
#   - EMAILS 40
#       - SEND EMAILS 15
#   - ADMIN PAGES 50
#   - MANAGEMENT 30

# - REGULAR 240
#   - INDEX 10
#       - CURRENT HUNT 780
#           - PUZZLE PAGES 450
#               - AJAX (LOG) 180,000
#               - PDF LINK 60
#               - SUBMIT ANSWER 450
#           - CHAT 111
#               - AJAX (LOG) 4830
#               - NEW MESSAGE 450
#       - INFO 27
#       - REGISTRATION 20
#           - UPDATE INFO 2
#       - RESOURCES 9
#       - PREVIOUS HUNTS 6
#           - OLD HUNT PAGES 15
#       - CREATE ACCOUNT 1
#       - CONTACT 1
#       - USER PROFILE 1
