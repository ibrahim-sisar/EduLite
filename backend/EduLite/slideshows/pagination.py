"""Pagination classes for the slideshows app."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SlideshowPagination(PageNumberPagination):
    """
    Standard pagination for slideshow listings.
    Optimized for browsing slideshows in discovery and user libraries.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "results": data,
                "page_size": self.page_size,
            }
        )
