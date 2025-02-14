from rest_framework.permissions import BasePermission


class IsPsychologist(BasePermission):
    """
    Allows access only to psychologists.
    """
    def has_permission(self, request, view):
        return request.user.user_type == 'psychologist'