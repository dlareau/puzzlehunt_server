# TEST PLAN
from locust import Locust, TaskSet, task, TaskSequence, seq_task
import sys

class StaffSet(TaskSet):

    @task(6)
    class staffChatSet(TaskSequence):
        @seq_task(1)
        def main_page(self):
            sys.stdout.write("chat main page")

        @seq_task(2)
        class ActionSet(TaskSet):

            @task(50)
            def new_message(self):
                sys.stdout.write("chat message page")

            @task(50)
            def ajax(self):
                sys.stdout.write("chat ajax request")

            @task(1)
            def stop(self):
                self.interrupt()

        @seq_task(3)
        def stop(self):
            self.interrupt()

    @task(7)
    class ProgressSet(TaskSequence):
        @seq_task(1)
        def main_page(self):
            sys.stdout.write("progress main page")

        @seq_task(2)
        class ActionSet(TaskSet):

            @task(50)
            def unlock(self):
                sys.stdout.write("progress unlock request")

            @task(50)
            def ajax(self):
                sys.stdout.write("progress ajax")

            @task(1)
            def stop(self):
                self.interrupt()

        @seq_task(3)
        def stop(self):
            self.interrupt()
       
    @task(8)
    class QueueSet(TaskSequence):
        @seq_task(1)
        def main_page(self):
            sys.stdout.write("queue main page")

        @seq_task(2)
        class ActionSet(TaskSet):

            @task(50)
            def numbered_page(self):
                sys.stdout.write("queue numbered page")

            @task(50)
            def new_response(self):
                sys.stdout.write("new response request")

            @task(50)
            def ajax(self):
                sys.stdout.write("queue ajax")

            @task(1)
            def stop(self):
                self.interrupt()

        @seq_task(3)
        def stop(self):
            self.interrupt()

    @task(2)
    class EmailSet(TaskSequence):
        @seq_task(1)
        def main_page(self):
            sys.stdout.write("email main page")

        @seq_task(2)
        class ActionSet(TaskSet):

            @task(50)
            def send_email(self):
                sys.stdout.write("send email request")

            @task(1)
            def stop(self):
                self.interrupt()

        @seq_task(3)
        def stop(self):
            self.interrupt()

    @task(1)
    def admin_page(self):
        sys.stdout.write("generic admin page")

    @task(2)
    def management(self):
        sys.stdout.write("management main page")

class MyLocust(Locust):
    task_set = StaffSet
    min_wait = 25
    max_wait = 30

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
#   - INDEX
#       - CURRENT HUNT 780
#           - PUZZLE PAGES
#               - AJAX (LOG)
#               - PDF LINK 4 
#               - SUBMIT ANSWER 30
#           - CHAT
#               - AJAX (LOG)
#               - NEW MESSAGE
#       - INFO 27
#       - REGISTRATION 20
#           - UPDATE INFO 2
#       - RESOURCES 9
#       - PREVIOUS HUNTS 6
#           - OLD HUNT PAGES
#       - CREATE ACCOUNT 1
#       - CONTACT 1
#       - USER PROFILE 1