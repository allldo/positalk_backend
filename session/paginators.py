from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 350

    def get_page_size(self, request):
        page_size = super().get_page_size(request)

        view = request.parser_context.get("view", None)
        if not view or not hasattr(view, "get_queryset"):
            return page_size

        queryset = view.get_queryset()
        count = queryset.count()

        paginator = self.django_paginator_class(queryset, page_size)
        total_pages = paginator.num_pages
        current_page = int(request.query_params.get(self.page_query_param, 1))

        if current_page == total_pages:
            remaining_items = count % page_size
            return remaining_items if remaining_items else page_size

        return page_size