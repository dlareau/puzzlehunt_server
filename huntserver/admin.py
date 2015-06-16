from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Hunt)
admin.site.register(Puzzle)
admin.site.register(Person)
admin.site.register(Team)
admin.site.register(Submission)