from typing import Union, Any
from typing import Optional
from functools import partial
from datetime import datetime, timedelta

import django_filters
from django.utils import timezone
from django.db.models import QuerySet

from .models import (
    Product,
    Order,
    OrderStatusChoices
)


TIMESTAMP_CHOICES = (
    ("today", "Today"),
    ("yesterday", "Yesterday",),
    ("last_week", "Last Week"),
    ("this_month", "This Month"),
    ("three_months", "3 Months Ago"),
    ("this_year", "This Year")
)

class ProductFilter(django_filters.FilterSet):

    class Meta:
        model = Product 
        fields = {
            "product_name": ["icontains"],
            "product_description": ["icontains"]
        }


class OrderFilter(django_filters.FilterSet):

    status = django_filters.ChoiceFilter(
        choices=OrderStatusChoices.choices,
        label="Status"
    )
    timestamp = django_filters.ChoiceFilter(
        choices=TIMESTAMP_CHOICES,
        label="Date",
        method="filter_by_date_choices"
    )

    class Meta:
        model = Order
        fields = ["status"]

    def filter_by_date_choices(
            self, 
            queryset: QuerySet, 
            name: str, 
            value: Optional[str]
        ) -> QuerySet:
        self.filter_timestamp = name
        today = timezone.now().date()
        parse_filter = partial(self._parse_timestamp_filter, queryset)
        match value:
            case "today":
                return (
                    parse_filter("date", today)
                    )
            case "yesterday":
                yesterday = today - timezone.timedelta(days=1)
                return (
                    parse_filter(
                        lookup="date",
                        value=yesterday
                    )
                )
            case "last_week":
                last_week = today - timedelta(weeks=1)
                return (
                    parse_filter(
                        "lte",
                        last_week
                    )
                )
            case "this_month":
                
                return (
                    parse_filter(
                        "month",
                        today.month,
                        **{f"{name}__year": today.year}
                    )
                )
            case "three_months":
                three_months = today - timezone.timedelta(days=90)
                return (
                    parse_filter(
                        "date",
                        three_months
                    )
                )
            case "this_year":
                return (
                    parse_filter(
                        "year",
                        today.year
                    )
                )

        return queryset

    def _parse_timestamp_filter(
            self, 
            queryset: QuerySet, 
            lookup: str, 
            value: Union[datetime, Any],
            **extra_kwargs
        ) -> QuerySet:
        filter_name = self.filter_timestamp
        lookup = self._build_lookup(filter_name, lookup)
        return queryset.filter(
            **{
                lookup: value,
                **extra_kwargs
            }
        )
    
    @property
    def filter_timestamp(self) -> str:
        
        if (filter_name := self._filter_field) is not None:
            return filter_name
        return "timestamp"

    @filter_timestamp.setter
    def filter_timestamp(self, value) -> None:
        self._filter_field = value

    def _build_lookup(self, name: str, lookup: Any, **kwargs) -> None:
        if lookup is None:
            return name
        return "%(name)s__%(lookup)s" % {"name": name, "lookup": lookup} # e.g timestamp__gte

