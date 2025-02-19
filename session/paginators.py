from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 350

    def get_page_size(self, request):
        page_size = super().get_page_size(request)
        count = self.page.paginator.count
        current_page = self.page.number
        total_pages = self.page.paginator.num_pages

        if current_page == total_pages:
            remaining_items = count % page_size
            return remaining_items if remaining_items else page_size

        return page_size