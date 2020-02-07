from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from huntserver.widgets import HtmlEditor
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe

# Register your models here.
from . import models


class UnlockableInline(admin.TabularInline):
    model = models.Unlockable
    extra = 1


class ResponseInline(admin.TabularInline):
    model = models.Response
    extra = 1


class UnlockInline(admin.TabularInline):
    model = models.Puzzle.unlocks.through
    extra = 2
    fk_name = 'to_puzzle'
    verbose_name = "Puzzle that counts towards unlocking this puzzle"
    verbose_name_plural = "Puzzles that count towards this puzzle"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_puzzle":
            try:
                parent_obj_id = request.resolver_match.args[0]
                puzzle = models.Puzzle.objects.get(id=parent_obj_id)
                query = models.Puzzle.objects.filter(hunt=puzzle.hunt)
                kwargs["queryset"] = query.order_by('puzzle_id')
            except IndexError:
                pass
        return super(UnlockInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class HintUnlockPlanForm(forms.ModelForm):
    class Meta:
        model = models.HintUnlockPlan
        fields = ('unlock_type', 'unlock_parameter')
        labels = {
            "unlock_type": "Unlock Type",
            "unlock_parameter": mark_safe("Unlock parameter:<div style='font-size: 8pt;'>"
                                          "Exact time: Number of minutes after hunt start</br>"
                                          "Interval: Number of minutes in the unlock interval</br>"
                                          "Solves: Number of puzzles to unlock a hint.</div>"),
        }


class HintUnlockPLanInline(admin.TabularInline):
    model = models.HintUnlockPlan
    extra = 2
    form = HintUnlockPlanForm


class PuzzleAdmin(admin.ModelAdmin):
    def get_object(self, request, object_id, to_field):
        # Hook obj for use in formfield_for_manytomany
        self.obj = super(PuzzleAdmin, self).get_object(request, object_id, to_field)
        return self.obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "unlocks" and getattr(self, 'obj', None):
            query = models.Puzzle.objects.filter(hunt=self.obj.hunt)
            kwargs["queryset"] = query.order_by('puzzle_id')
        return super(PuzzleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    list_filter = ('hunt',)
    fields = ('hunt', 'puzzle_name', 'puzzle_number', 'puzzle_id', 'is_meta',
              'doesnt_count', 'is_html_puzzle', 'resource_link', 'link', 'solution_link',
              'answer', 'extra_data', 'num_pages', 'num_required_to_unlock')
    inlines = (UnlockInline, ResponseInline)


class PrepuzzleAdminForm(forms.ModelForm):
    model = models.Prepuzzle

    class Meta:
        fields = '__all__'
        widgets = {
            'template': HtmlEditor(attrs={'style': 'width: 90%; height: 400px;'}),
        }


class PrepuzzleAdmin(admin.ModelAdmin):
    form = PrepuzzleAdminForm
    readonly_fields = ('puzzle_url',)

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
        fields = ['team_name', 'unlocked', 'unlockables', 'hunt', 'location',
                  'join_code', 'playtester', 'num_available_hints']

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
    list_filter = ('hunt',)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_shib_acct',)
    search_fields = ['user__email', 'user__username', 'user__first_name', 'user__last_name']


class HuntAdminForm(forms.ModelForm):
    model = models.Hunt

    class Meta:
        fields = '__all__'
        widgets = {
            'template': HtmlEditor(attrs={'style': 'width: 90%; height: 400px;'}),
        }


class HuntAdmin(admin.ModelAdmin):
    form = HuntAdminForm
    inlines = (HintUnlockPLanInline,)


class UserProxyObject(User):
    class Meta:
        proxy = True
        app_label = 'huntserver'
        verbose_name = User._meta.verbose_name
        verbose_name_plural = User._meta.verbose_name_plural


class UserProxyAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username', 'first_name', 'last_name']


admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(UserProxyObject, UserProxyAdmin)
admin.site.register(models.Hunt, HuntAdmin)
admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Prepuzzle, PrepuzzleAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Submission)
admin.site.register(models.Solve)
admin.site.register(models.Unlock)
admin.site.register(models.Message)
admin.site.register(models.Response)
admin.site.register(models.Unlockable)
admin.site.register(models.Hint)
