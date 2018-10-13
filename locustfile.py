# TEST PLAN
from locust import HttpLocust, TaskSet, TaskSequence
from bs4 import BeautifulSoup, SoupStrainer
import random
from string import ascii_lowercase
import sys
import re

# TODO:
#   Write staff url functions
#   Write puzzle_submit_answer url function
#   Modify current_hunt request to only look at unsolved puzzles
#   Add name arguments to all ajax requests

# Server TODO:
#   Make sure all post requests return proper ajax value
#   Make sure all ajax requests end in a slash
#   Chat page of a public hunt 404's
#   Fix chat announcement and whois bugs


# ========== HELPTER FUNCTIONS/VARIABLES ==========

puzzle_answers = {
    201: "answer1",
    202: "answer2",
    203: "answer3",
    204: "answer4",
    205: "answer5",
    206: "answer6",
    207: "answer7",
    208: "answer8",
    209: "answer9",
    210: "answer10",
    211: "answer11",
    212: "answer12",
    213: "answer13",
    214: "answer14",
    215: "answer15",
    216: "answer16",
}


def random_string(n):
    return ''.join(random.choice(ascii_lowercase) for i in range(n))


def is_puzzle_link(link):
        return link and "/puzzle/" in link


only_puzzles = SoupStrainer(href=is_puzzle_link)


def is_hunt_link(link):
        return link and "/hunt/" in link


only_hunts = SoupStrainer(href=is_hunt_link)


ajax_headers = {'X-Requested-With': 'XMLHttpRequest'}


def CSRF_post(session, url, args):
    session.client.headers['Referer'] = session.client.base_url
    args['csrfmiddlewaretoken'] = session.locust.CSRF
    response = session.client.post(url, args,
                                   headers={"X-CSRFToken": session.locust.CSRF},
                                   cookies={"csrftoken": session.locust.CSRF})
    return response


def page_and_subpages(main_function, action_set):
    class ActionSet(TaskSet):
        tasks = action_set

    class ts(TaskSequence):
        tasks = [main_function, ActionSet, stop]

    return ts


def add_static(session, response, cache=True):
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
        if(url not in session.locust.static_urls):
            session.locust.static_urls.add(url)

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

        if("/accounts/login/" in response.url):
            # Login failed
            sys.stdout.write("login-failed")

        return response
    else:
        return input_response
    pass


def store_CSRF(session, response):
    if('csrftoken' in response.cookies):
        session.locust.CSRF = response.cookies['csrftoken']
    return response


def url_all(l, r):
    return add_static(l, ensure_login(l, store_CSRF(l, r)))


def stop(l):
    l.interrupt()

# ========== END HELPTER FUNCTIONS/VARIABLES ==========


# ========== HUNTER PAGE VIEW FUNCTIONS ==========

def index(l):
    # Load index page
    url_all(l, l.client.get("/"))


def current_hunt_main_page(l):
    # Load page, get puzzles, set puzzles on locust object
    # Possibly separate by solved and unsolved
    response = url_all(l, l.client.get("/hunt/current/"))

    puzzle_ids = []
    soup = BeautifulSoup(response.text, "html.parser", parse_only=only_puzzles)
    for puzzle_link in soup.find_all(href=True):
        puzzle_ids.append(puzzle_link['href'].split("/")[2])

    l.locust.puzzle_ids = puzzle_ids


def puzzle_main_page(l):
    # Pick puzzle from puzzles, go to page, possibly weight by solved/unsolved
    # Store current puzzle number in locust object
    # Get ajax number from page and store to locust object
    puzzle_id = random.choice(l.locust.puzzle_ids)
    l.locust.puzzle_id = puzzle_id
    response = url_all(l, l.client.get("/puzzle/" + puzzle_id))
    search_results = re.search(r"last_date = '(.*)';", response.text)
    if(search_results):
        last_date = search_results.group(1)
    else:
        last_date = ""
    l.locust.ajax_args = {'last_date': last_date}


def puzzle_ajax(l):
    # make request to current puzzle object with current ajax number
    # store returned ajax number in locust object
    puzzle_id = l.locust.puzzle_id
    response = l.client.get("/puzzle/" + puzzle_id + "/?last_date=" + l.locust.ajax_args['last_date'],
                            headers=ajax_headers)
    try:
        l.locust.ajax_args = {'last_date': response.json()["last_date"]}
    except:
        l.locust.ajax_args = {'last_date': ""}


def puzzle_pdf_link(l):
    # Load pdf link for current puzzle number
    puzzle_id = l.locust.puzzle_id
    l.client.get("/protected/puzzles/" + puzzle_id + ".pdf")


def puzzle_answer(l):
    # Submit answer to current puzzle using POST with some correctness chance
    # 1 in 9 submissions is correct
    sys.stdout.write("submit answer request")


def chat_main_page(l):
    # Load main chat page and store ajax value in locust object
    response = url_all(l, l.client.get("/chat/"))

    search_results = re.search(r"last_pk = (.*);", response.text)
    if(search_results):
        last_pk = search_results.group(1)
    else:
        last_pk = ""
    l.locust.ajax_args = {'last_pk': last_pk}

    search_results = re.search(r"curr_team = (.*);", response.text)
    if(search_results):
        curr_team = search_results.group(1)
    else:
        curr_team = ""
    l.locust.team_pk = curr_team


def chat_ajax(l):
    # Make ajax request with current ajax value and store new value
    response = l.client.get("/chat/?last_pk=" + str(l.locust.ajax_args['last_pk']),
                            headers=ajax_headers)
    try:
        l.locust.ajax_args = {'last_pk': response.json()["last_pk"]}
    except:
        l.locust.ajax_args = {'last_pk': ""}


def chat_new_message(l):
    # Make POST request to create a new chat message, store ajax value
    message_data = {
        "team_pk": int(l.locust.team_pk),
        "message": random_string(40),
        "is_response": False,
        "is_announcement": False
    }
    store_CSRF(l, CSRF_post(l, "/chat/", message_data))


def info_main_page(l):
    # Load info page
    url_all(l, l.client.get("/hunt/info/"))


def registration_main_page(l):
    # Load registration page
    url_all(l, l.client.get("/registration/"))


def registration_update_info(l):
    # Update the teams room location
    registration_data = {
        "form type": "new_location",
        "team_location": random_string(10)
    }
    store_CSRF(l, CSRF_post(l, "/registration/", registration_data))


def resources(l):
    # Load resources page
    url_all(l, l.client.get("/resources/"))


def previous_hunts_main_page(l):
    # Load previous hunts page, store list of available hunts in locust object
    response = url_all(l, l.client.get("/hunt/current/"))

    hunt_ids = []
    soup = BeautifulSoup(response.text, "html.parser", parse_only=only_hunts)
    for hunt_link in soup.find_all(href=True):
        hunt_ids.append(hunt_link['href'].split("/")[2])

    l.locust.hunt_ids = hunt_ids


def previous_hunt(l):
    # Load a random previous hunt page in the locust object
    hunt_id = random.choice(l.locust.hunt_ids)
    url_all(l, l.client.get("/hunt/" + hunt_id))


def create_account(l):
    # Load the create account page
    url_all(l, l.client.get("/accounts/create/"))


def contact(l):
    # Load contact page
    url_all(l, l.client.get("/contact/"))


def user_profile(l):
    # Load user profile page
    url_all(l, l.client.get("/user-profile/"))

# ========== END HUNTER PAGE VIEW FUNCTIONS ==========


# ========== STAFF PAGE VIEW FUNCTIONS ==========

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

# ========== END STAFF PAGE VIEW FUNCTIONS ==========


# ========== PAGE VIEW PROBABILITIES ==========

staff_chat_fs = {staff_chat_new_message: 3, staff_chat_ajax: 80, stop: 1}
progress_fs = {progress_unlock: 1, progress_ajax: 150, stop: 4}
queue_fs = {queue_num_page: 1, queue_new_response: 6, queue_ajax: 1000, stop: 3}
email_fs = {email_send_email: 1, stop: 2}

# puzzle_fs = {puzzle_ajax: 3000, puzzle_pdf_link: 1, puzzle_answer: 8, stop: 8}
puzzle_fs = {puzzle_ajax: 30, puzzle_pdf_link: 1, puzzle_answer: 8, stop: 8}
chat_fs = {chat_ajax: 40, chat_new_message: 4, stop: 1}
current_hunt_fs = {page_and_subpages(puzzle_main_page, puzzle_fs): 4,
                   page_and_subpages(chat_main_page, chat_fs): 100,
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

    def on_start(self):
        self.locust.static_urls = set()


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

    def on_start(self):
        self.locust.static_urls = set()

# ========== END PAGE VIEW PROBABILITIES ==========


# ========== USERS CODE ==========

# Staff user
class StaffLocust(HttpLocust):
    task_set = StaffSet
    min_wait = 2500
    max_wait = 3000
    weight = 10


# Regular user
class HunterLocust(HttpLocust):
    task_set = HunterSet
    min_wait = 1000
    max_wait = 1000
    weight = 240

# ========== END USERS CODE ==========
