from locust import HttpLocust, TaskSet, TaskSequence, between, constant
from bs4 import BeautifulSoup, SoupStrainer
from string import ascii_lowercase
import random
import gevent
import sys
import re

# TODO:
#   Modify current_hunt request to only look at unsolved puzzles
#   Fix no last_pk error with chat post (user and staff)

# ========== HELPTER FUNCTIONS/VARIABLES ==========
thread_list = []
kill_list = []

num_bots = 900
num_staff = int(num_bots / 25)
num_users = num_bots - num_staff
user_ids = list(range(num_users))
staff_ids = list(range(num_users, num_users + num_staff))

USER_PASSWORD = "password"


def get_status(greenlets):
    total = 0
    running = 0
    completed = 0
    successed = 0
    yet_to_run = 0
    failed = 0

    for g in greenlets:
        total += 1
        if bool(g):
            running += 1
            if(g in kill_list):
                sys.stdout.write("Attempting to kill!")
                g.kill(block=True)
        else:
            if g.ready():
                completed += 1
                if g.successful():
                    successed += 1
                else:
                    failed += 1
            else:
                yet_to_run += 1

    assert yet_to_run == total - completed - running
    assert failed == completed - successed

    return dict(total=total,
                running=running,
                completed=completed,
                successed=successed,
                yet_to_run=yet_to_run,
                failed=failed)


def random_string(n):
    return ''.join(random.choice(ascii_lowercase) for i in range(n))


def is_puzzle_link(link):
    return link and "/puzzle/" in link


only_puzzles = SoupStrainer(href=is_puzzle_link)


def is_hunt_link(link):
    return link and "/hunt/" in link


only_hunts = SoupStrainer(href=is_hunt_link)


ajax_headers = {'X-Requested-With': 'XMLHttpRequest'}


def set_ajax_args(l, attr, val):
    # sys.stdout.write("User-id: %d, setting: %s" % (l.locust.user_id, str(val)))
    l.locust.ajax_args[attr] = val


def get_ajax_args(l, attr):
    # sys.stdout.write("User-id: %d, getting: %s" % (l.locust.user_id, str(l.locust.ajax_args)))
    return l.locust.ajax_args[attr]


def better_get(l, url, **kwargs):
    # return l.client.get(url, **dict(timeout=None, **kwargs))
    return l.client.get(url, **kwargs)


def gen_from_list(in_list):
    index = 0
    length = len(in_list)
    while True:
        if(index < length):
            yield in_list[index]
        else:
            yield in_list[index - 1]


def gevent_func(poller, l):
    try:
        while True:
            poller.ajax_func(l)
            a = next(poller.time_iter)
            gevent.sleep(a)
    except gevent.GreenletExit:
        # sys.stdout.write("Got GreenletExit exception from %d" % l.locust.user_id)
        return


class Poller(object):
    thread = None
    ajax_vars = None

    def __init__(self, ajax_func, delay_list):
        self.ajax_func = ajax_func
        self.delay_list = delay_list
        self.time_iter = gen_from_list(delay_list)

    def reset_time_iter(self):
        self.time_iter = gen_from_list(self.delay_list)


def apply_poller(task_set, poller):
    def poller_on_start(ts):
        poller.thread = gevent.spawn(gevent_func, poller, ts)
        thread_list.append(poller.thread)
        ts.locust.poller = poller
        # sys.stdout.write("Started thread %d" % ts.locust.user_id)
        # sys.stdout.write(str(get_status(thread_list)))
        # sys.stdout.write("KILL:" + str(get_status(kill_list)))

    def poller_on_stop(ts):
        kill_list.append(poller.thread)
        sys.stdout.write(str(len(kill_list)))
        poller.thread.kill(block=True)
        # sys.stdout.write("Ended thread %d" % ts.locust.user_id)

    if(poller):
        task_set.on_start = poller_on_start
        task_set.on_stop = poller_on_stop

    return task_set


def page_and_subpages(main_function, action_set, poller=None, time=None):
    class ActionSet(TaskSet):
        tasks = action_set
        if(time):
            wait_time = constant(time)

    class ts(TaskSequence):
        tasks = [main_function, apply_poller(ActionSet, poller), stop]
        if(poller):
            wait_time = constant(1)

    return ts


def add_static(session, response, cache=True):
    # Fetches all static resources from a response
    if(response.text):
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

    if(input_response.url and
       ("login-selection" in input_response.url or "/staff/login/" in input_response.url)):
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
        store_CSRF(session, response)
        args = {"username": "test_user_" + str(session.locust.user_id),
                "password": USER_PASSWORD + str(session.locust.user_id)
                }

        response = store_CSRF(session, CSRF_post(session, next_url, args))

        if("/accounts/login/" in response.url or "/staff/login/" in response.url):
            # Login failed
            sys.stdout.write("login-failed")

        return response
    else:
        return input_response
    pass


def store_CSRF(session, response):
    # sys.stdout.write("|STORED CSRF: " + response.url)
    if(response.cookies and 'csrftoken' in response.cookies):
        session.locust.client.cookies.set('csrftoken', None)
        session.locust.client.cookies.set('csrftoken', response.cookies['csrftoken'])
        session.locust.templateCSRF = session.locust.client.cookies['csrftoken']
        # sys.stdout.write("|    COOKIE:   " + session.locust.client.cookies['csrftoken'])

    search_results = re.search(r"csrf_token = '(.*?)';", response.text)
    if(search_results):
        session.locust.templateCSRF = search_results.group(1)
        # sys.stdout.write("|    TEMPLATE: " + session.locust.templateCSRF)
    search_results = re.search(r"name='csrfmiddlewaretoken' value='(.*?)'", response.text)
    if(search_results):
        session.locust.templateCSRF = search_results.group(1)
        # sys.stdout.write("|    TEMPLATE: " + session.locust.templateCSRF)
    return response


def CSRF_post(session, url, args):
    session.client.headers['Referer'] = session.client.base_url
    args['csrfmiddlewaretoken'] = session.locust.templateCSRF
    response = session.client.post(url, args,
                                   headers={"X-CSRFToken": session.locust.templateCSRF})
    if(response.status_code == 403):
        sys.stdout.write("|403 FAILURE: " + response.url)
        sys.stdout.write(str("|    COOKIE:   " + str(session.locust.client.cookies.items())))
        sys.stdout.write(str("|    TEMPLATE: " + session.locust.templateCSRF))
        sys.stdout.write(str("|    " + str(response.request.headers)))
        sys.stdout.write(str("|    " + str(response.request.body)))
        sys.stdout.write(str("|    " + str(response.text)))
    return response


def url_all(l, r):
    return add_static(l, ensure_login(l, store_CSRF(l, r)))


def stop(l):
    if(hasattr(l, 'on_stop')):
        l.on_stop()
    l.interrupt()

# ========== END HELPTER FUNCTIONS/VARIABLES ==========


# ========== HUNTER PAGE VIEW FUNCTIONS ==========

def index(l):
    # Load index page
    url_all(l, better_get(l, "/"))


def current_hunt_main_page(l):
    # Load page, get puzzles, set puzzles on locust object
    # Possibly separate by solved and unsolved
    response = url_all(l, better_get(l, "/hunt/current/"))

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
    response = url_all(l, better_get(l, "/puzzle/" + puzzle_id + "/"))
    search_results = re.search(r"last_date = '(.*)';", response.text)
    if(search_results):
        last_date = search_results.group(1)
    else:
        sys.stdout.write("puzzle_main_page could not find ajax last date: %s" % str(response.text))
        sys.stdout.flush()
        last_date = ""
    set_ajax_args(l, "puzzle", {'last_date': last_date})


def puzzle_ajax(l):
    # make request to current puzzle object with current ajax number
    # store returned ajax number in locust object
    if(get_ajax_args(l, "puzzle")['last_date'] == ""):
        print("Cowardly refusing to send empty ajax last date")
        return
    puzzle_id = l.locust.puzzle_id
    puzzle_url = "/puzzle/" + puzzle_id + "/"
    response = better_get(l, puzzle_url + "?last_date=" + get_ajax_args(l, "puzzle")['last_date'],
                          headers=ajax_headers, name=puzzle_url + " AJAX")
    try:
        set_ajax_args(l, "puzzle", {'last_date': response.json()["last_date"]})
    except:
        sys.stdout.write("puzzle_ajax could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        pass


def puzzle_pdf_link(l):
    # Load pdf link for current puzzle number
    puzzle_id = l.locust.puzzle_id
    better_get(l, "/protected/puzzles/" + puzzle_id + ".pdf")


def puzzle_answer(l):
    # Submit answer to current puzzle using POST with some correctness chance
    # 1 in 9 submissions is correct
    puzzle_id = l.locust.puzzle_id
    if(random.random() < (1.0 / 9.0)):
        answer = "answer" + puzzle_id
    else:
        answer = random_string(10)

    message_data = {"answer": answer}
    store_CSRF(l, CSRF_post(l, "/puzzle/" + puzzle_id + "/", message_data))
    l.locust.poller.reset_time_iter()


def chat_main_page(l):
    # Load main chat page and store ajax value in locust object
    response = url_all(l, better_get(l, "/chat/"))

    search_results = re.search(r"last_pk = (.*);", response.text)
    if(search_results):
        last_pk = search_results.group(1)
    else:
        sys.stdout.write("chat_main_page could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        last_pk = ""
    set_ajax_args(l, "chat", {'last_pk': last_pk})

    search_results = re.search(r"curr_team = (.*);", response.text)
    if(search_results):
        curr_team = search_results.group(1)
    else:
        curr_team = ""
    l.locust.team_pk = curr_team


def chat_ajax(l):
    # Make ajax request with current ajax value and store new value
    response = better_get(l, "/chat/?last_pk=" + str(get_ajax_args(l, "chat")['last_pk']),
                          headers=ajax_headers, name="/chat/ AJAX")
    try:
        set_ajax_args(l, "chat", {'last_pk': response.json()["last_pk"]})
    except:
        sys.stdout.write("chat_ajax could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        pass


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
    url_all(l, better_get(l, "/hunt-info/"))


def registration_main_page(l):
    # Load registration page
    url_all(l, better_get(l, "/registration/"))


def registration_update_info(l):
    # Update the teams room location
    registration_data = {
        "form type": "new_location",
        "team_location": random_string(10)
    }
    store_CSRF(l, CSRF_post(l, "/registration/", registration_data))


def resources(l):
    # Load resources page
    url_all(l, better_get(l, "/info/extra/resources/"))


def previous_hunts_main_page(l):
    # Load previous hunts page, store list of available hunts in locust object
    response = url_all(l, better_get(l, "/previous-hunts/"))

    hunt_ids = []
    soup = BeautifulSoup(response.text, "html.parser", parse_only=only_hunts)
    for hunt_link in soup.find_all(href=True):
        hunt_ids.append(hunt_link['href'].split("/")[2])

    l.locust.hunt_ids = hunt_ids


def previous_hunt(l):
    # Load a random previous hunt page in the locust object
    hunt_id = random.choice(l.locust.hunt_ids)
    url_all(l, better_get(l, "/hunt/" + hunt_id))


def create_account(l):
    # Load the create account page
    url_all(l, better_get(l, "/accounts/create/"))


def contact(l):
    # Load contact page
    url_all(l, better_get(l, "/contact-us/"))


def user_profile(l):
    # Load user profile page
    url_all(l, better_get(l, "/user-profile/"))

# ========== END HUNTER PAGE VIEW FUNCTIONS ==========


# ========== STAFF PAGE VIEW FUNCTIONS ==========

def staff_chat_main_page(l):
    # Load main chat page and store ajax value in locust object
    response = url_all(l, better_get(l, "/staff/chat/"))

    search_results = re.search(r"last_pk = (.*);", response.text)
    if(search_results):
        last_pk = search_results.group(1)
    else:
        sys.stdout.write("staff_chat_main_page could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        last_pk = ""
    set_ajax_args(l, "staff_chat", {'last_pk': last_pk})

    search_results = re.findall(r"data-id='(.*)' ", response.text)
    if(search_results):
        l.locust.staff_chat_teams = search_results
    else:
        l.locust.staff_chat_teams = None


def staff_chat_new_message(l):
    # Make POST request to create a new chat message, store ajax value
    if(l.locust.staff_chat_teams):
        message_data = {
            "team_pk": int(random.choice(l.locust.staff_chat_teams)),
            "message": random_string(40),
            "is_response": True,
            "is_announcement": False
        }
        store_CSRF(l, CSRF_post(l, "/staff/chat/", message_data))


def staff_chat_ajax(l):
    # Make ajax request with current ajax value and store new value
    response = better_get(l, "/staff/chat/?last_pk=" + str(get_ajax_args(l, "staff_chat")['last_pk']),
                          headers=ajax_headers, name="/staff/chat/ AJAX")
    try:
        set_ajax_args(l, "staff_chat", {'last_pk': response.json()["last_pk"]})
    except:
        sys.stdout.write("staff_chat_ajax could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        pass


def progress_main_page(l):
    response = url_all(l, better_get(l, "/staff/progress/"))
    search_results = re.search(r"last_solve_pk = (.*);\n *last_unlock_pk = (.*);\n *last_submission_pk = (.*)", response.text)
    if(search_results):
        set_ajax_args(l, "progress", {
            'last_solve_pk': search_results.group(1),
            'last_unlock_pk': search_results.group(2),
            'last_submission_pk': search_results.group(3),
        })
    else:
        sys.stdout.write("progress_main_page could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        set_ajax_args(l, "progress", {
            'last_solve_pk': 0,
            'last_unlock_pk': 0,
            'last_submission_pk': 0,
        })

    search_results = re.findall(r"id='p(.*)t(.*)' class='unavailable'", response.text)
    if(search_results):
        l.locust.progress_info = search_results
    else:
        l.locust.progress_info = None


def progress_unlock(l):
    if(l.locust.progress_info and len(l.locust.progress_info) > 0):
        puzzle_info = random.choice(l.locust.progress_info)
        l.locust.progress_info.remove(puzzle_info)
        message_data = {
            "team_id": int(puzzle_info[1]),
            "puzzle_id": puzzle_info[0],
            "action": "unlock"
        }
        store_CSRF(l, CSRF_post(l, "/staff/progress/", message_data))


def progress_ajax(l):
    response = better_get(l, "/staff/progress/?" +
        "last_solve_pk=" + str(get_ajax_args(l, "progress")['last_solve_pk']) +
        "&last_unlock_pk=" + str(get_ajax_args(l, "progress")['last_unlock_pk']) +
        "&last_submission_pk=" + str(get_ajax_args(l, "progress")['last_submission_pk']),
        headers=ajax_headers, name="/staff/progress/ AJAX")
    try:
        update_info = response.json()["update_info"]
        if(len(update_info) > 0):
            set_ajax_args(l, "progress", {
                'last_solve_pk': update_info[0],
                'last_unlock_pk': update_info[1],
                'last_submission_pk': update_info[2],
            })
    except:
        sys.stdout.write("progress_ajax could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        pass


def queue_main_page(l):
    response = url_all(l, better_get(l, "/staff/queue/"))
    search_results = re.search(r"last_date = '(.*)';", response.text)
    if(search_results):
        last_date = search_results.group(1)
    else:
        sys.stdout.write("queue_main_page could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
    set_ajax_args(l, "queue", {'last_date': last_date})

    search_results = re.search(r"incorrect-replied *\n *submission.*data-id='(\d+)'>", response.text)
    if(search_results):
        l.locust.queue_sub_id = search_results.group(1)
    else:
        l.locust.queue_sub_id = None


def queue_num_page(l):
    url_all(l, better_get(l, "/staff/queue/?page_num=1"))


def queue_new_response(l):
    if(l.locust.queue_sub_id):
        message_data = {
            "response": random_string(40),
            "sub_id": l.locust.queue_sub_id
        }
        store_CSRF(l, CSRF_post(l, "/staff/queue/", message_data))


def queue_ajax(l):
    response = better_get(l, "/staff/queue/?last_date=" + str(get_ajax_args(l, "queue")['last_date']) + "&all=true",
                          headers=ajax_headers, name="/staff/queue/ AJAX")
    try:
        set_ajax_args(l, "queue", {'last_date': response.json()["last_date"]})
    except:
        sys.stdout.write("queue_ajax could not find ajax: %s" % str(response.text))
        sys.stdout.flush()
        pass


def email_main_page(l):
    url_all(l, better_get(l, "/staff/emails/"))


def admin_page(l):
    url_all(l, better_get(l, "/staff/huntserver/hunt/"))
    url_all(l, better_get(l, "/staff/huntserver/hunt/9/change/"))


def management(l):
    url_all(l, better_get(l, "/staff/management/"))

# ========== END STAFF PAGE VIEW FUNCTIONS ==========


# ========== PAGE VIEW PROBABILITIES ==========
# These numbers come from a experimental and finicky verification process
# Changing one number could have unintended effects on the rates for other pages
# They are also specifically tuned to specific request times (30, 130, 1200)

staff_chat_fs = {
    staff_chat_new_message: 98,
    stop:                   27
}

progress_fs = {
    progress_unlock:    27,
    stop:               98
}

queue_fs = {
    queue_num_page:     17,
    queue_new_response: 104,
    stop:               45
}

puzzle_fs = {
    puzzle_pdf_link:    2,
    puzzle_answer:      15,
    stop:               15
}

chat_fs = {
    chat_new_message:   9,
    stop:               11
}

current_hunt_fs = {
    page_and_subpages(puzzle_main_page, puzzle_fs,
                      Poller(puzzle_ajax, [3, 8, 20, 47, 117, 120]),
                      1060000):                     54,
    page_and_subpages(chat_main_page, chat_fs,
                      Poller(chat_ajax, [3]),
                      130000):                      11,
    stop:                                           78
}

registration_fs = {
    registration_update_info:   1,
    stop:                       10
}

prev_hunt_fs = {
    previous_hunt:  5,
    stop:           2
}


class StaffSet(TaskSet):
    tasks = {
        page_and_subpages(staff_chat_main_page, staff_chat_fs,
                          Poller(staff_chat_ajax, [3]),
                          70000):                               15,
        page_and_subpages(progress_main_page, progress_fs,
                          Poller(progress_ajax, [3]),
                          465000):                              27,
        page_and_subpages(queue_main_page, queue_fs,
                          Poller(queue_ajax, [3]),
                          418000):                              32,
        email_main_page:                                        8,
        admin_page:                                             2,
        management:                                             6
    }

    def on_start(self):
        self.locust.static_urls = set()
        self.locust.user_id = staff_ids.pop()
        self.locust.ajax_args = {}


class WebsiteSet(TaskSet):
    tasks = {
        page_and_subpages(current_hunt_main_page,
                          current_hunt_fs):         780,
        page_and_subpages(registration_main_page,
                          registration_fs):         20,
        page_and_subpages(previous_hunts_main_page,
                          prev_hunt_fs):            6,
        info_main_page:                             27,
        resources:                                  9,
        create_account:                             1,
        contact:                                    1,
        user_profile:                               1,
        stop:                                       70
    }


class HunterSet(TaskSequence):
    tasks = [index, WebsiteSet]

    def on_start(self):
        self.locust.static_urls = set()
        self.locust.user_id = user_ids.pop()
        self.locust.ajax_args = {}

# ========== END PAGE VIEW PROBABILITIES ==========


# ========== USERS CODE ==========

# Staff user
class StaffLocust(HttpLocust):
    task_set = StaffSet
    wait_time = between(100, 140)
    weight = 10


# Regular user
class HunterLocust(HttpLocust):
    task_set = HunterSet
    wait_time = between(20, 40)
    weight = 240

# ========== END USERS CODE ==========
