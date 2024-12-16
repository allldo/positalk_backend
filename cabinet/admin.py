from django.contrib import admin

from cabinet.models import CustomUser, PhoneVerification

admin.site.register(CustomUser)
admin.site.register(PhoneVerification)