from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return OrderedDict(
            [
                ("count", self.page.paginator.count),
                ("page_size", self.page.paginator.per_page),
                ("pages", self.page.paginator.num_pages),
                ("results", data),
            ]
        )

    def get_paginated_response_schema(self, schema):
        schema["properties"].extend(
            {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "page_size": {
                    "type": "integer",
                    "example": 123,
                },
                "pages": {
                    "type": "integer",
                    "example": 123,
                },
            }
        )
        return schema
