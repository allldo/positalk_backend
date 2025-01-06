from django.contrib import admin

from cabinet.models import CustomUser, PhoneVerification, Survey

admin.site.register(CustomUser)
admin.site.register(PhoneVerification)
admin.site.register(Survey)