from django.contrib import admin

# Register your models here.
from .models import *

class PuzzleAdmin(admin.ModelAdmin):
    filter_horizontal = ('unlocks',)

class PersonInline(admin.TabularInline):
    model = Person
    extra = 5
    max_num = 5 

class TeamAdmin(admin.ModelAdmin):
    inlines = (PersonInline, )
    filter_horizontal = ('unlocked',)
    
admin.site.register(Hunt)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Person)
admin.site.register(Team, TeamAdmin)
admin.site.register(Submission)
