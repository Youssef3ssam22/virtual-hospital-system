"""shared/utils/pagination.py — Standard DRF pagination."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from shared.domain.exceptions import InvalidOperation


class StandardPagination(PageNumberPagination):
    """Default pagination for all list endpoints.

    Query parameters:
        ?page=1     — page number (1-based)
        ?limit=20   — items per page (max 100)

    Response envelope:
        {
            "total":     150,
            "page":      2,
            "limit":     20,
            "pages":     8,
            "has_next":  true,
            "has_prev":  true,
            "next_page": 3,
            "prev_page": 1,
            "items":     [...]
        }
    """
    page_size             = 20
    page_size_query_param = "limit"
    max_page_size         = 100
    page_query_param      = "page"

    def get_paginated_response(self, data):
        return Response({
            "total":     self.page.paginator.count,
            "page":      self.page.number,
            "limit":     self.get_page_size(self.request),
            "pages":     self.page.paginator.num_pages,
            "has_next":  self.page.has_next(),
            "has_prev":  self.page.has_previous(),
            "next_page": self.page.next_page_number()     if self.page.has_next()     else None,
            "prev_page": self.page.previous_page_number() if self.page.has_previous() else None,
            "items":     data,
        })

    def get_paginated_response_schema(self, schema):
        """Register the response shape with drf-spectacular for correct API docs."""
        return {
            "type": "object",
            "properties": {
                "total":     {"type": "integer"},
                "page":      {"type": "integer"},
                "limit":     {"type": "integer"},
                "pages":     {"type": "integer"},
                "has_next":  {"type": "boolean"},
                "has_prev":  {"type": "boolean"},
                "next_page": {"type": "integer", "nullable": True},
                "prev_page": {"type": "integer", "nullable": True},
                "items":     schema,
            },
        }


def paginate_queryset(qs, page: int, limit: int) -> tuple:
    """Offset-based pagination for QuerySets used outside DRF views.

    FIX: was not validating page/limit — page=0 or negative values
    produced negative offsets which PostgreSQL treats as 0, returning
    all rows silently instead of raising an error.

    Returns (sliced_queryset, total_count).

    Usage:
        items, total = paginate_queryset(qs, page=2, limit=25)
    """
    page  = int(page)
    limit = int(limit)

    if page < 1:
        raise InvalidOperation("Page number must be 1 or greater")
    if limit < 1:
        raise InvalidOperation("Limit must be 1 or greater")
    if limit > 200:
        raise InvalidOperation("Limit cannot exceed 200")

    total  = qs.count()
    offset = (page - 1) * limit
    return qs[offset: offset + limit], total