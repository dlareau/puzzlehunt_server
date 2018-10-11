# TEST PLAN
from locust import Locust, TaskSet, task, TaskSequence, seq_task
import sys

def stop(l):
    l.interrupt()

def page_and_subpages(main_function, action_set):
    class ActionSet(TaskSet):
        tasks = action_set

    class ts(TaskSequence):
        tasks = [main_function, ActionSet, stop]

    return ts


# All of the page view functions
def staff_chat_main_page(l):
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


def index(l):
    sys.stdout.write("index page")


def current_hunt_main_page(l):
    sys.stdout.write("current hunt main page")


def puzzle_main_page(l):
    sys.stdout.write("individual puzzle main page")

def puzzle_ajax(l):
    sys.stdout.write("puzzle ajax request")

def puzzle_pdf_link(l):
    sys.stdout.write("puzzle pdf request")

def puzzle_answer(l):
    sys.stdout.write("submit answer request")


def chat_main_page(l):
    sys.stdout.write("chat main page")

def chat_ajax(l):
    sys.stdout.write("chat ajax request")

def chat_new_message(l):
    sys.stdout.write("chat new message request")


def info_main_page(l):
    sys.stdout.write("info page")


def registration_main_page(l):
    sys.stdout.write("registration main page")

def registration_update_info(l):
    sys.stdout.write("update team info request")


def resources(l):
    sys.stdout.write("resource page")


def previous_hunts_main_page(l):
    sys.stdout.write("previous hunts main page")

def previous_hunt(l):
    sys.stdout.write("previous hunt page")


def create_account(l):
    sys.stdout.write("create account page")


def contact(l):
    sys.stdout.write("contact page")


def user_profile(l):
    sys.stdout.write("user profile page")


# All of the probabilty stuff
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
class StaffLocust(Locust):
    task_set = StaffSet
    min_wait = 2500
    max_wait = 3000
    weight = 10

# Regular user
class HunterLocust(Locust):
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
