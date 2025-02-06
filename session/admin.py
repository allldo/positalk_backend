from django.contrib import admin

from session.models import Session, TimeSlot

admin.site.register(Session)
admin.site.register(TimeSlot)