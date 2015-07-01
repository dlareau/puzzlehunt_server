from django.contrib import admin

# Register your models here.
from .models import *

class PuzzleAdmin(admin.ModelAdmin):
    filter_horizontal = ('unlocks',)

class SolveInline(admin.TabularInline):
    model = Solve
    extra = 2

class TeamAdmin(admin.ModelAdmin):
    inlines = (SolveInline,)
    
admin.site.register(Hunt)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Person)
admin.site.register(Team, TeamAdmin)
admin.site.register(Submission)
