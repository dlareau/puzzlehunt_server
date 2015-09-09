from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
from .models import *
import json
from django.utils.html import escape
from django.core import serializers
from django.conf import settings
from django.utils.dateformat import DateFormat
from dateutil import tz
time_zone = tz.gettz(settings.TIME_ZONE)

# Sends an update on an answer submission to staff and the submitter
# Is called usually after any modification to the submission
def send_submission_update(submission):
    redis_publisher = RedisPublisher(facility='puzzle_submissions',
             users=[submission.team.login_info.username, settings.ADMIN_ACCTS[0]])
    modelJSON = json.loads(serializers.serialize("json", [submission]))[0]
    message = modelJSON['fields']
    message['response_text'] = escape(message['response_text'])
    message['puzzle'] = submission.puzzle.puzzle_id
    message['puzzle_name'] = submission.puzzle.puzzle_name
    message['team'] = submission.team.team_name
    message['pk'] = modelJSON['pk']
    df = DateFormat(submission.submission_time.astimezone(time_zone))
    message['time_str'] = df.format("h:i a")
    message = RedisMessage(json.dumps(message))
    redis_publisher.publish_message(message)

# Sends an update to staff and a team about when a puzzle is solved or unlocked
# This does not actually solve or unlock anything, and relies on there actually
# being a solve or unlock object, so please call appropriately
def send_status_update(puzzle, team, status_type):
    # status_type should be either "solve" or "unlock"
    redis_publisher = RedisPublisher(facility='puzzle_status',
                                     users=[team.login_info.username, settings.ADMIN_ACCTS[0]])
    message = dict()
    message['puzzle_id'] = puzzle.puzzle_id
    message['puzzle_num'] = puzzle.puzzle_number
    message['puzzle_name'] = puzzle.puzzle_name
    message['team_pk'] = team.pk
    message['status_type'] = status_type
    if(status_type == 'solve'):
        time = team.solve_set.filter(puzzle=puzzle)[0].submission.submission_time
        df = DateFormat(time.astimezone(time_zone))
        message['time_str'] = df.format("h:i a")
    message = RedisMessage(json.dumps(message))
    redis_publisher.publish_message(message)

# Displays a chat message to the relevant users
def send_chat_message(message):
    redis_publisher = RedisPublisher(facility='chat_message',
                      users=[settings.ADMIN_ACCT[0], message.team.login_info.username])
    packet = dict()
    packet['team_pk'] = message.team.pk
    packet['team_name'] = message.team.team_name
    packet['text'] = message.text
    packet['is_response'] = message.is_response
    df = DateFormat(message.time.astimezone(time_zone))
    packet['time'] = df.format("h:i a")
    packet = RedisMessage(json.dumps(packet))
    redis_publisher.publish_message(packet)
