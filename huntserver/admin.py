import inspect
import re

from django import forms
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User, Group
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.template.defaultfilters import truncatechars
from django.urls import re_path
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from huntserver.widgets import HtmlEditor

from .utils import get_validation_error, get_puzzle_answer_regex
from . import models
from . import staff_views


def short_team_name(teamable_object):
    return truncatechars(teamable_object.team.team_name, 50)


short_team_name.short_description = "Team name"


class HintAdmin(admin.ModelAdmin):
    list_display = [short_team_name, 'puzzle', 'request_time', 'has_been_answered']

    def has_been_answered(self, hint):
        return hint.response != ""

    has_been_answered.boolean = True
    has_been_answered.short_description = "Answered?"


class HintUnlockPlanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HintUnlockPlanForm, self).__init__(*args, **kwargs)
        self.fields['unlock_parameter'].help_text = ("Exact time: Number of minutes after hunt "
                                                     "start</br>Interval: Number of minutes in the "
                                                     "unlock interval</br> Solves: Number of "
                                                     "puzzles to unlock a hint.")


class HintUnlockPLanInline(admin.TabularInline):
    model = models.HintUnlockPlan
    extra = 2
    form = HintUnlockPlanForm
    fields = ['unlock_type', 'unlock_parameter']
    radio_fields = {"unlock_type": admin.VERTICAL}


class HuntAdminForm(forms.ModelForm):
    model = models.Hunt

    class Meta:
        widgets = {
            'template': HtmlEditor(attrs={'style': 'width: 90%; height: 400px;'}),
        }


class HuntAdmin(admin.ModelAdmin):
    form = HuntAdminForm
    inlines = (HintUnlockPLanInline,)
    ordering = ['-hunt_number']
    fieldsets = (
        ('Basic Info', {'fields': ('hunt_name', 'hunt_number', 'team_size', 'location',
                        ('start_date', 'display_start_date'), ('end_date', 'display_end_date'),
                        'is_current_hunt')}),
        ('Hunt Behaviour', {'fields': ('points_per_minute', 'hint_lockout')}),
        ('Resources/Template', {'fields': ('resource_file', 'extra_data', 'template')}),
    )

    list_display = ['hunt_name', 'team_size', 'start_date', 'is_current_hunt']


class MessageAdmin(admin.ModelAdmin):
    list_display = [short_team_name, 'short_message']
    search_fields = ['text']
    autocomplete_fields = ['team']

    def short_message(self, message):
        return truncatechars(message.text, 60)

    short_message.short_description = "Message"


class PersonAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'user_username', 'is_shib_acct']
    search_fields = ['user__email', 'user__username', 'user__first_name', 'user__last_name']
    filter_horizontal = ['teams']

    def user_full_name(self, person):
        return person.user.first_name + " " + person.user.last_name

    def user_username(self, person):
        return person.user.username

    user_full_name.short_description = "Name"
    user_username.short_description = "Username"


class PrepuzzleAdminForm(forms.ModelForm):
    class Meta:
        model = models.Prepuzzle
        fields = ['puzzle_name', 'released', 'hunt', 'answer', 'answer_validation_type',
                  'resource_file', 'template', 'response_string']
        widgets = {
            'template': HtmlEditor(attrs={'style': 'width: 90%; height: 400px;'}),
        }


class PrepuzzleAdmin(admin.ModelAdmin):
    form = PrepuzzleAdminForm
    list_display = ['puzzle_name', 'hunt', 'released', 'answer_validation_type']
    readonly_fields = ('puzzle_url',)

    # Needed to add request to modelAdmin
    def get_queryset(self, request):
        qs = super(PrepuzzleAdmin, self).get_queryset(request)
        self.request = request
        return qs

    def puzzle_url(self, obj):
        puzzle_url_str = "http://" + self.request.get_host() + "/prepuzzle/" + str(obj.pk) + "/"
        html = "<script> function myFunction() { "
        html += "var copyText = document.getElementById('puzzleURL'); "
        html += "copyText.select(); "
        html += "document.execCommand('copy'); } </script>"
        html += "<input style='width: 400px;' type=\"text\""
        html += "value=\"" + puzzle_url_str + "\" id=\"puzzleURL\">"
        html += "<button onclick=\"myFunction()\" type=\"button\">Copy Puzzle URL</button>"
        return mark_safe(html)

    puzzle_url.short_description = 'Puzzle URL: (Not editable)'


class UnlockInline(admin.TabularInline):
    model = models.Puzzle.unlocks.through
    extra = 2
    fk_name = 'to_puzzle'
    verbose_name = "Puzzle that counts towards unlocking this puzzle"
    verbose_name_plural = "Puzzles that count towards this puzzle"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_puzzle":
            try:
                parent_obj_id = request.resolver_match.kwargs['object_id']
                puzzle = models.Puzzle.objects.get(id=parent_obj_id)
                query = models.Puzzle.objects.filter(hunt=puzzle.hunt)
                kwargs["queryset"] = query.order_by('puzzle_id')
            except IndexError:
                pass
        return super(UnlockInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ResponseInline(admin.TabularInline):
    model = models.Response
    extra = 1


class PuzzleAdminForm(forms.ModelForm):
    reverse_unlocks = forms.ModelMultipleChoiceField(
        models.Puzzle.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Puzzle', False),
        required=False,
        label="Puzzles that count towards this puzzle"
    )

    def __init__(self, *args, **kwargs):
        super(PuzzleAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['reverse_unlocks'] = self.instance.puzzle_set.values_list('pk', flat=True)
            choices = self.instance.hunt.puzzle_set.values_list('pk', 'puzzle_name')
            self.fields['reverse_unlocks'].choices = choices

    def save(self, *args, **kwargs):
        instance = super(PuzzleAdminForm, self).save(*args, **kwargs)
        if instance.pk:
            instance.puzzle_set.clear()
            instance.puzzle_set.add(*self.cleaned_data['reverse_unlocks'])
        return instance

    def clean(self):
        data = self.cleaned_data
        answer = data.get('answer')
        validation_type = data.get('answer_validation_type')
        if(validation_type == models.Puzzle.ANSWER_STRICT):
            data['answer'] = answer.upper()
        if(re.fullmatch(get_puzzle_answer_regex(validation_type), answer) is None):
            self.add_error('answer', forms.ValidationError(get_validation_error(validation_type)))
        return data

    class Meta:
        model = models.Puzzle
        fields = ('hunt', 'puzzle_name', 'puzzle_number', 'puzzle_id', 'answer',
                  'answer_validation_type', 'puzzle_type', 'puzzle_page_type', 'puzzle_file',
                  'resource_file', 'solution_file', 'extra_data', 'num_required_to_unlock',
                  'unlock_type', 'points_cost', 'points_value', 'solution_is_webpage',
                  'solution_resource_file')


class PuzzleAdmin(admin.ModelAdmin):
    class Media:
        js = ("huntserver/admin_change_puzzle.js",)

    form = PuzzleAdminForm

    list_filter = ('hunt',)
    search_fields = ['puzzle_id', 'puzzle_name']
    list_display = ['combined_id', 'puzzle_name', 'hunt', 'puzzle_type']
    list_display_links = ['combined_id', 'puzzle_name']
    ordering = ['-hunt', 'puzzle_number']
    inlines = (ResponseInline,)
    radio_fields = {"unlock_type": admin.VERTICAL}
    fieldsets = (
        (None, {
            'fields': ('hunt', 'puzzle_name', 'answer', 'answer_validation_type', 'puzzle_number',
                       'puzzle_id', 'puzzle_type', 'puzzle_page_type', 'puzzle_file', 'resource_file',
                       'solution_is_webpage', 'solution_file', 'solution_resource_file',
                       'extra_data', 'unlock_type')
        }),
        ('Solve Unlocking', {
            'classes': ('formset_border', 'solve_unlocking'),
            'fields': ('reverse_unlocks', 'num_required_to_unlock')
        }),
        ('Points Unlocking', {
            'classes': ('formset_border', 'points_unlocking'),
            'fields': ('points_cost', 'points_value')
        }),
    )

    def combined_id(self, puzzle):
        return str(puzzle.puzzle_number) + "-" + puzzle.puzzle_id

    combined_id.short_description = "ID"


class ResponseAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'puzzle_just_name']
    search_fields = ['regex', 'text']

    def puzzle_just_name(self, response):
        return response.puzzle.puzzle_name

    puzzle_just_name.short_description = "Puzzle"


class SolveAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'solve_time']
    autocomplete_fields = ['team', 'submission']

    def solve_time(self, solve):
        return solve.submission.submission_time


class SubmissionAdmin(admin.ModelAdmin):
    search_fields = ['submission_text']
    list_display = ['submission_text', short_team_name, 'submission_time']
    autocomplete_fields = ['team']


class TeamAdminForm(forms.ModelForm):
    persons = forms.ModelMultipleChoiceField(
        queryset=models.Person.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('People'),
            is_stacked=False
        )
    )

    num_unlock_points = forms.IntegerField(disabled=True, initial=0)

    class Meta:
        model = models.Team
        fields = ['team_name', 'hunt', 'location', 'join_code', 'playtester', 'is_local',
                  'playtest_start_date', 'playtest_end_date', 'num_available_hints',
                  'num_unlock_points', 'unlockables']

    def __init__(self, *args, **kwargs):
        super(TeamAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['persons'].initial = self.instance.person_set.all()

    def save(self, commit=True):
        team = super(TeamAdminForm, self).save(commit=False)

        if commit:
            team.save()

        if team.pk:
            team.person_set.set(self.cleaned_data['persons'])
            self.save_m2m()

        return team


class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    search_fields = ['team_name']
    list_display = ['short_team_name', 'hunt', 'is_local', 'playtester']
    list_filter = ['hunt']

    def short_team_name(self, team):
        return truncatechars(team.team_name, 30) + " (" + str(team.size) + ")"

    short_team_name.short_description = "Team name"


class UnlockAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'time']
    autocomplete_fields = ['team']


class UserProxyObject(User):
    class Meta:
        proxy = True
        app_label = 'huntserver'
        verbose_name = User._meta.verbose_name
        verbose_name_plural = User._meta.verbose_name_plural
        ordering = ['-pk']


class UserProxyAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name']
    search_fields = ['email', 'username', 'first_name', 'last_name']


class FlatPageProxyObject(FlatPage):
    class Meta:
        proxy = True
        app_label = 'huntserver'
        verbose_name = "info page"
        verbose_name_plural = "info pages"


class FlatpageProxyForm(FlatpageForm):
    class Meta:
        model = FlatPageProxyObject
        fields = '__all__'


# Define a new FlatPageAdmin
class FlatPageProxyAdmin(FlatPageAdmin):
    list_filter = []
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content')}),
        (None, {
            'classes': ('hidden',),
            'fields': ('sites',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (
                'registration_required',
                'template_name',
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = FlatpageProxyForm
        form = super(FlatPageAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['sites'].initial = Site.objects.get(pk=1)
        form.base_fields['content'].widget = HtmlEditor(attrs={'style': 'width:90%; height:400px;'})
        form.base_fields['url'].help_text = ("Example: '/contact-us/' translates to " +
                                             "/info/contact-us/. Make sure to have leading and " +
                                             "trailing slashes.")
        return form


class StaffPagesAdmin(AdminSite):
    """A Django AdminSite with the ability to register custom staff pages not connected to models."""
    # Pattern taken from django adminplus from jsocol

    def __init__(self, *args, **kwargs):
        self.custom_views = []
        return super(StaffPagesAdmin, self).__init__(*args, **kwargs)

    def register_view(self, path, name=None, urlname=None, visible=True, view=None):
        self.custom_views.append((path, view, name, urlname, visible))

    def get_urls(self):
        urls = super(StaffPagesAdmin, self).get_urls()
        for path, view, name, urlname, visible in self.custom_views:
            urls.insert(0, re_path(r"^%s$" % path, self.admin_view(view), name=urlname))
        return urls

    def get_app_list(self, request, app_label=None):
        app_list = super(StaffPagesAdmin, self).get_app_list(request)
        app_list.insert(0, {
            "name": "Staff Pages",
            "app_label": "staff-pages",
            "app_url": "/staff/",
            "has_module_perms": True,
            "models": [
                {
                    "model": None,
                    "name": name if name else capfirst(view.__name__),
                    "object_name": view.__name__,
                    "perms": {},
                    "admin_url": path,
                    "add_url": None,
                    "view_only": True
                } for path, view, name, urlname, visible in self.custom_views if visible
            ]
        })
        return app_list


huntserver_admin = StaffPagesAdmin()
huntserver_admin.register_view('queue/', view=staff_views.queue, urlname='queue')
huntserver_admin.register_view('progress/', view=staff_views.progress, urlname='progress')
huntserver_admin.register_view('charts/', view=staff_views.charts, urlname='charts')
huntserver_admin.register_view('chat/', view=staff_views.admin_chat, name="Chat", urlname='admin_chat')
huntserver_admin.register_view('emails/', view=staff_views.emails, urlname='emails')
huntserver_admin.register_view('management/', view=staff_views.hunt_management, name="Hunt Management", urlname='hunt_management')
huntserver_admin.register_view('hints/', view=staff_views.staff_hints_text, name="Hints", urlname='staff_hints_text')
huntserver_admin.register_view('info/', view=staff_views.hunt_info, name="Hunt Info", urlname='hunt_info')
huntserver_admin.register_view('lookup/', view=staff_views.lookup, urlname='lookup')

huntserver_admin.register_view('control/', view=staff_views.control, urlname='control', visible=False)
huntserver_admin.register_view('hints/control/', view=staff_views.staff_hints_control, urlname='staff_hints_control', visible=False)

# path('teams/', RedirectView.as_view(url='/admin/huntserver/team/', permanent=False)),
# path('puzzles/', RedirectView.as_view(url='/admin/huntserver/puzzle/', permanent=False)),

huntserver_admin.register(models.Hint,       HintAdmin)
huntserver_admin.register(models.Hunt,       HuntAdmin)
huntserver_admin.register(models.Message,    MessageAdmin)
huntserver_admin.register(models.Person,     PersonAdmin)
huntserver_admin.register(models.Prepuzzle,  PrepuzzleAdmin)
huntserver_admin.register(models.Puzzle,     PuzzleAdmin)
huntserver_admin.register(models.Response,   ResponseAdmin)
huntserver_admin.register(models.Solve,      SolveAdmin)
huntserver_admin.register(models.Submission, SubmissionAdmin)
huntserver_admin.register(models.Team,       TeamAdmin)
huntserver_admin.register(models.Unlockable)
huntserver_admin.register(models.Unlock,     UnlockAdmin)
huntserver_admin.register(UserProxyObject,   UserProxyAdmin)
huntserver_admin.register(FlatPageProxyObject, FlatPageProxyAdmin)