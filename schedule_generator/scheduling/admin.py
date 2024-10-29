from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Subject)
admin.site.register(Room)
admin.site.register(LectureRoom)
admin.site.register(Laboratories)
admin.site.register(PEGymHall)
admin.site.register(Timeslot)


