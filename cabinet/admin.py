from django.contrib import admin

from cabinet.models import CustomUser, PhoneVerification, Survey, PsychologistSurvey, Education

admin.site.register(CustomUser)
admin.site.register(PhoneVerification)
admin.site.register(Education)
admin.site.register(Survey)
admin.site.register(PsychologistSurvey)