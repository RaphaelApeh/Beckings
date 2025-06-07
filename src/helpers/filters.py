from __future__ import annotations

from typing import TypeVar, Optional

from django.db import models
from django.db.models import Q
from django.db.models import QuerySet
from django.template.loader import get_template

from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.filters import BaseFilterBackend

from ._typing import LookUp


View = TypeVar("View", GenericAPIView, APIView)


def qs_vector_search(model: type[models.Model],
                    query: Optional[str]) -> QuerySet:
    
    assert issubclass(model, models.Model)

    manager = model.objects
    
    if not query:
        return manager.none()
    
    queryset = manager.search(query)
    return queryset


def qs_filter(model: models.Model, query: Optional[str], 
              lookup: LookUp = "icontains") -> QuerySet:

    search_fields = getattr(model, "SEARCH_FIELDS", ())
    search_fields = (*search_fields, "user__username")
    q = Q()
    qs = model.objects.select_related("user")
    
    if not query:
        return qs.all() # return all queryset
    
    for field in search_fields:
        
        q |= Q(**{f"{field}__{lookup}": query})
    
    qs = qs.filter(q)
    
    return qs


class ModelSearchFilterBackend(BaseFilterBackend):


    def filter_queryset(self, request: Request, queryset: QuerySet, view: View) -> QuerySet:
        
        search_query = getattr(view, "search_query", "q")
        
        query = request.query_params.get(search_query, "")
        
        model = queryset.model
        
        if getattr(view, "use_vector_search", False):
            return qs_vector_search(model, query)
        
        return qs_filter(model, query)
    

    def to_html(self, request: Request, queryset: QuerySet, view: View) -> str:

        context = {}
        
        search_query = getattr(view, "search_query", "q")

        template = get_template("_filter_query.html")
        context["search_query"] = search_query
        return template.render(context, request)
    


