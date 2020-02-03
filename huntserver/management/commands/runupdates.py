from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import F

from huntserver.models import Hunt, HintUnlockPlan


class Command(BaseCommand):
    help = 'Runs all time related updates for the huntserver app'

    def handle(self, *args, **options):
        # Check hints
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
        num_min = (timezone.now() - curr_hunt.start_date).seconds / 60
        for hup in curr_hunt.hintunlockplan_set.exclude(unlock_type=HintUnlockPlan.SOLVES_UNLOCK):
            if((hup.unlock_type == hup.TIMED_UNLOCK
               and hup.num_triggered < 1
               and num_min > hup.unlock_parameter)
               or (hup.unlock_type == hup.INTERVAL_UNLOCK
               and num_min / hup.unlock_parameter < hup.num_triggered)):
                curr_hunt.team_set.all().update(num_available_hints=F('num_available_hints') + 1)
                hup.num_triggered = hup.num_triggered + 1
                hup.save()
