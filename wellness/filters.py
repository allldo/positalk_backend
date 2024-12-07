from rest_framework.filters import BaseFilterBackend


class CaseInsensitiveSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_param = request.query_params.get('search', '')
        if search_param:
            return queryset.filter(title__icontains=search_param)
        return queryset