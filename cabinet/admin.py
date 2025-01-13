from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from cabinet.models import CustomUser, PhoneVerification, Survey, PsychologistSurvey, Education


admin.site.register(PhoneVerification)
admin.site.register(Education)
admin.site.register(Survey)
admin.site.register(PsychologistSurvey)


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone_number',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )

    list_display = ('phone_number',)
    search_fields = ('phone_number',)
    ordering = ('phone_number',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.set_unusable_password()
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)