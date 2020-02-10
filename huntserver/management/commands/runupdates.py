from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F
from datetime import datetime

from huntserver.models import Hunt, HintUnlockPlan


class Command(BaseCommand):
    help = 'Runs all time related updates for the huntserver app'

    def handle(self, *args, **options):
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
        if(not curr_hunt.is_open):
            return

        last_update_time = curr_hunt.last_update_time.replace(second=0, microsecond=0)
        curr_hunt.last_update_time = timezone.now()
        curr_hunt.save()
        diff_time = timezone.now().replace(second=0, microsecond=0) - last_update_time
        diff_minutes = diff_time.seconds / 60

        # Check hints
        num_min = (timezone.now() - curr_hunt.start_date).seconds / 60
        for hup in curr_hunt.hintunlockplan_set.exclude(unlock_type=HintUnlockPlan.SOLVES_UNLOCK):
            if((hup.unlock_type == hup.TIMED_UNLOCK and
               hup.num_triggered < 1 and num_min > hup.unlock_parameter)
               or (hup.unlock_type == hup.INTERVAL_UNLOCK and
               num_min / hup.unlock_parameter < hup.num_triggered)):
                curr_hunt.team_set.all().update(num_available_hints=F('num_available_hints') + 1)
                hup.num_triggered = hup.num_triggered + 1
                hup.save()

        # Check puzzles
        if(diff_minutes >= 1):
            new_points = curr_hunt.points_per_minute * diff_minutes
            curr_hunt.team_set.all().update(num_unlock_points=F('num_unlock_points') + new_points)
            #for team in curr_hunt.team_set.all():
                #unlockable_puzzles = curr_hunt.puzzle_set.exclude()
                # write function on puzzle that takes team and checks if it is/should be unlocked
                # filter out all puzzles that can't possibly be unlocked because time then run the
                # unlock function on each of them