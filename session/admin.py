from django.contrib import admin

from session.models import Session, TimeSlot, Message, Chat

admin.site.register(Session)
admin.site.register(TimeSlot)
admin.site.register(Chat)
admin.site.register(Message)