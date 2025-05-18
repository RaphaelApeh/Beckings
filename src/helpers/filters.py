from typing import TypeVar

from django.db.models import Q
from django.db.models import QuerySet
from django.template.loader import get_template

from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.filters import BaseFilterBackend


View = TypeVar("View", GenericAPIView, APIView)


class ModelSearchFilterBackend(BaseFilterBackend):


    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        search_query = getattr(view, "search_query", "q")
        query = request.query_params.get(search_query, "")
        model = queryset.model
        manager = model.objects
        search_fields = getattr(model, "SEARCH_FIELDS", ())
        if query:
            if hasattr(manager, "search"):
                queryset = manager.search(query)
            else:
                q = Q()
                for field in search_fields:
                    q |= Q(**{field: query})
                queryset = queryset.filter(q)
        return queryset
    

    def to_html(self, request: Request, queryset: QuerySet, view: View) -> str:

        context = {}

        template = get_template("_filter_query.html")
        return template.render(context, request)
    


