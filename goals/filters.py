from django.db import models
from django_filters import (
    IsoDateTimeFilter,
    rest_framework
)

from goals.models import Goal


class GoalDateFilter(rest_framework.FilterSet):
    class Meta:
        model = Goal
        fields = {
            'due_date': ('lte', 'gte'),
            'category': ('exact', 'in'),
            'status': ('exact', 'in'),
            'priority': ('exact', 'in'),
        }

    filter_overrides = {
        models.DateTimeField: {'filter_class': IsoDateTimeFilter},
    }
