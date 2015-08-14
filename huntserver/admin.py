from django.contrib import admin

# Register your models here.
from .models import *

class UnlockableInline(admin.TabularInline):
    model = Unlockable
    extra = 1

class PuzzleAdmin(admin.ModelAdmin):
    list_filter = ('hunt',)
    inlines = (UnlockableInline, )
    
class PersonInline(admin.TabularInline):
    model = Person
    extra = 5
    max_num = 5 

class TeamAdmin(admin.ModelAdmin):
    inlines = (PersonInline, )
    list_filter = ('hunt',)
    
admin.site.register(Hunt)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Person)
admin.site.register(Team, TeamAdmin)
admin.site.register(Submission)
admin.site.register(Solve)
admin.site.register(Unlock)
admin.site.register(Message)