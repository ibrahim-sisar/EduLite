"""Pagination classes for the courses app."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CoursePagination(PageNumberPagination):
    """
    Standard pagination for course listings.
    Optimized for browsing courses in discovery and user libraries.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """Override to store the actual page size being used."""
        self.request = request
        # Store the actual page size for this request
        self._current_page_size = self.get_page_size(request)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "results": data,
                "page_size": getattr(self, "_current_page_size", self.page_size),
            }
        )
