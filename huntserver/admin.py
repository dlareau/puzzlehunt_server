from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple

# Register your models here.
import models

class UnlockableInline(admin.TabularInline):
    model = models.Unlockable
    extra = 1

class PuzzleAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "unlocks":
            kwargs["queryset"] = models.Puzzle.objects.filter(hunt=models.Hunt.objects.get(is_current_hunt=True)).order_by('puzzle_id')
        return super(PuzzleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    list_filter = ('hunt',)
    filter_horizontal = ('unlocks',)

class TeamAdminForm(forms.ModelForm):
    persons = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('People'),
            is_stacked=False
        )
    )

    class Meta:
        model = models.Team
        fields = ['team_name', 'unlocked', 'unlockables', 'hunt', 'location', 'join_code', 'playtester']

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

admin.site.register(models.Hunt)
admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Person)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Submission)
admin.site.register(models.Solve)
admin.site.register(models.Unlock)
admin.site.register(models.Message)
admin.site.register(models.Response)
admin.site.register(models.Unlockable)