from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class CaseInsensitiveSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search', None)
        if search_query:
            regex = rf".*{search_query}.*"
            queryset = queryset.filter(Q(title__iregex=regex))
        return queryset