from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F

from huntserver.models import Hunt, HintUnlockPlan


def check_hints(hunt):
    num_min = (timezone.now() - hunt.start_date).seconds / 60
    for hup in hunt.hintunlockplan_set.exclude(unlock_type=HintUnlockPlan.SOLVES_UNLOCK):
        if((hup.unlock_type == hup.TIMED_UNLOCK and
           hup.num_triggered < 1 and num_min > hup.unlock_parameter) or
           (hup.unlock_type == hup.INTERVAL_UNLOCK and
           num_min / hup.unlock_parameter < hup.num_triggered)):
            hunt.team_set.all().update(num_available_hints=F('num_available_hints') + 1)
            hup.num_triggered = hup.num_triggered + 1
            hup.save()


def check_puzzles(hunt, new_points, teams):
    teams.update(num_unlock_points=F('num_unlock_points') + new_points)
    for team in teams:
        team.unlock_puzzles()


class RunUpdates(BaseCommand):
    help = 'Runs all time related updates for the huntserver app'

    def handle(self, *args, **options):
        hunt = Hunt.objects.get(is_current_hunt=True)

        last_update_time = hunt.last_update_time.replace(second=0, microsecond=0)
        hunt.last_update_time = timezone.now()
        hunt.save()
        diff_time = timezone.now().replace(second=0, microsecond=0) - last_update_time
        diff_minutes = diff_time.seconds / 60

        if(hunt.is_open):
            check_hints

        if(diff_minutes >= 1):
            new_points = hunt.points_per_minute * diff_minutes

            if(hunt.is_open):
                check_puzzles(hunt, new_points, hunt.team_set.all())
            else:
                playtesters = hunt.team_set.filter(playtester=True).all()
                playtesters = [t for t in playtesters if t.playtest_happening]
                if(len(playtesters) > 0):
                    check_puzzles(hunt, new_points, playtesters)
