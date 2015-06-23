from django.contrib import admin

# Register your models here.
from .models import *

class PuzzleAdmin(admin.ModelAdmin):
    filter_horizontal = ('unlocks',)

admin.site.register(Hunt)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Person)
admin.site.register(Team)
admin.site.register(Submission)
