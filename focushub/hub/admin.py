from django.contrib import admin
from . models import Task, Habit, HabitLog, FocusSession

admin.site.register(Task)
admin.site.register(Habit)
admin.site.register(HabitLog)
admin.site.register(FocusSession)