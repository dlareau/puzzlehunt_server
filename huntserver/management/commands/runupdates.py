from django.core.management.base import BaseCommand
from django.utils import timezone

from huntserver.models import Hunt


class Command(BaseCommand):
    help = 'Runs all time related updates for the huntserver app'

    def handle(self, *args, **options):
        # Check hints
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
        for hup in curr_hunt.hintunlockplan_set.all():
            if(hup.unlock_type == hup.TIMED_UNLOCK):
                if(hup.num_triggered < 1):
                    num_min = (timezone.now() - curr_hunt.start_date).seconds / 60
                    if(num_min > hup.unlock_parameter):
                        for team in curr_hunt.team_set.all():
                            team.num_available_hints = team.num_available_hints + 1
                        hup.num_triggered = hup.num_triggered + 1
            elif(hup.unlock_type == hup.INTERVAL_UNLOCK):
                num_min = (timezone.now() - curr_hunt.start_date).seconds / 60
                if(num_min / hup.unlock_parameter < hup.num_triggered):
                    for team in curr_hunt.team_set.all():
                        team.num_available_hints = team.num_available_hints + 1
                    hup.num_triggered = hup.num_triggered + 1
