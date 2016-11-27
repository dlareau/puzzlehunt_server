from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple

# Register your models here.
from .models import Hunt, Person, Team, Submission, Solve, Unlock, Puzzle, Message, Unlockable
from django.conf import settings

class UnlockableInline(admin.TabularInline):
    model = Unlockable
    extra = 1

class PuzzleAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "unlocks":
            kwargs["queryset"] = Puzzle.objects.filter(hunt=Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)).order_by('puzzle_id')
        return super(PuzzleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    list_filter = ('hunt',)
    filter_horizontal = ('unlocks',)

class TeamAdminForm(forms.ModelForm):
    persons = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('People'),
            is_stacked=False
        )
    )

    class Meta:
        model = Team
        fields = ['team_name', 'unlocked', 'unlockables', 'hunt', 'location', 'join_code']

    def __init__(self, *args, **kwargs):
        super(TeamAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['persons'].initial = self.instance.person_set.all()

    def save(self, commit=True):
        team = super(TeamAdminForm, self).save(commit=False)

        if commit:
            team.save()

        if team.pk:
            team.person_set = self.cleaned_data['persons']
            self.save_m2m()

        return team

class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    list_filter = ('hunt',)

admin.site.register(Hunt)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Person)
admin.site.register(Team, TeamAdmin)
admin.site.register(Submission)
admin.site.register(Solve)
admin.site.register(Unlock)
admin.site.register(Message)
