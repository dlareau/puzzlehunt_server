from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from huntserver.widgets import HtmlEditor
from django.contrib.auth.models import User, Group

# Register your models here.
from . import models

class UnlockableInline(admin.TabularInline):
    model = models.Unlockable
    extra = 1

class ResponseInline(admin.TabularInline):
    model = models.Response
    extra = 1
#    template = "admin/tabular_custom.html"

class UnlockInline(admin.TabularInline):
    model = models.Puzzle.unlocks.through
    extra = 2
    fk_name = 'to_puzzle'
    verbose_name = "Puzzle that counts towards unlocking this puzzle"
    verbose_name_plural = "Puzzles that count towards this puzzle"
#    template = "admin/tabular_custom.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_puzzle":
            try:
                parent_obj_id = request.resolver_match.args[0]
                puzzle = models.Puzzle.objects.get(id=parent_obj_id)
                kwargs["queryset"] = models.Puzzle.objects.filter(hunt=puzzle.hunt).order_by('puzzle_id')
            except IndexError:
                pass
        return super(UnlockInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class PuzzleAdmin(admin.ModelAdmin):
    def get_object(self, request, object_id, to_field):
        # Hook obj for use in formfield_for_manytomany
        self.obj = super(PuzzleAdmin, self).get_object(request, object_id, to_field)
        return self.obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "unlocks" and getattr(self, 'obj', None):
            kwargs["queryset"] = models.Puzzle.objects.filter(hunt=self.obj.hunt).order_by('puzzle_id')
        return super(PuzzleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    list_filter = ('hunt',)
    fields = ('hunt', 'puzzle_name', 'puzzle_number', 'puzzle_id', 'is_meta', 
              'is_html_puzzle', 'resource_link', 'link', 'answer',
              'num_pages', 'num_required_to_unlock')
    inlines = (UnlockInline, ResponseInline)

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

class PersonAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_shib_acct',)
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

class HuntAssetFileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'url')
    readonly_fields = ('url',)

    def url(self, obj):
        return obj.file.url

class UserProxyObject(User):
    class Meta:
        proxy = True
        app_label = 'huntserver'
        verbose_name = User._meta.verbose_name
        verbose_name_plural = User._meta.verbose_name_plural

admin.site.unregister(User)
admin.site.unregister(Group)
        
admin.site.register(UserProxyObject)
admin.site.register(models.Hunt, HuntAdmin)
admin.site.register(models.Puzzle, PuzzleAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Submission)
admin.site.register(models.Solve)
admin.site.register(models.Unlock)
admin.site.register(models.Message)
admin.site.register(models.Response)
admin.site.register(models.Unlockable)
admin.site.register(models.HuntAssetFile, HuntAssetFileAdmin)
