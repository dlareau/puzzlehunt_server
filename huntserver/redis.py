from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
from .models import *
import json
from django.core import serializers
from django.conf import settings
from django.utils.dateformat import DateFormat

def send_submission_update(submission):
    redis_publisher = RedisPublisher(facility='puzzle_submissions',
             users=[submission.team.login_info.username, settings.ADMIN_ACCT])
    modelJSON = json.loads(serializers.serialize("json", [submission]))[0]
    message = modelJSON['fields']
    message['puzzle'] = submission.puzzle.puzzle_id
    message['puzzle_name'] = submission.puzzle.puzzle_name
    message['team'] = submission.team.team_name
    message['pk'] = modelJSON['pk']
    message = RedisMessage(json.dumps(message))
    redis_publisher.publish_message(message)

def send_status_update(puzzle, team, status_type):
    # status_type should be either "solve" or "unlock"
    redis_publisher = RedisPublisher(facility='puzzle_status',
                                     users=[team.login_info.username, settings.ADMIN_ACCT])
    message = dict()
    message['puzzle_id'] = puzzle.puzzle_id
    message['puzzle_num'] = puzzle.puzzle_number
    message['puzzle_name'] = puzzle.puzzle_name
    message['team_pk'] = team.pk
    message['status_type'] = status_type
    if(status_type == 'solve'):
        time = team.solve_set.filter(puzzle=puzzle)[0].submission.submission_time
        df = DateFormat(time)
        message['time_str'] = df.format("h:i a")
    message = RedisMessage(json.dumps(message))
    redis_publisher.publish_message(message)