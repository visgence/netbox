import django_filters
import netaddr
from django.core.exceptions import ValidationError
from django.db.models import Q
from netaddr.core import AddrFormatError

from extras.filters import CustomFieldFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import NameSlugSearchFilterSet, NumericInFilter, TagFilter
from .constants import EXTENSION_STATUS_CHOICES
from .models import Extension, Partition, Line
from dcim.models import Device

class ExtensionFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    dn = django_filters.CharFilter(
        method='filter_dn',
        label='Extension',
    )
    partition_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Partition.objects.all(),
        label='Partition',
    )
    line = django_filters.ModelMultipleChoiceFilter(
        field_name='line__name',
        queryset=Line.objects.all(),
        to_field_name='name',
        label='Line (ID)',
    )
    line_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Line.objects.all(),
        label='Line (ID)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=EXTENSION_STATUS_CHOICES,
        null_value=None
    )
    tag = TagFilter()

    class Meta:
        model = Extension
        fields = ['dn', 'partition']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(description__icontains=value) |
            Q(dn__istartswith=value)
        )
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(value.strip())
            return queryset.filter(dn_contained=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def filter_dn(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            return queryset.filter(dn__icontains=value)
        except ValidationError:
            return queryset.none()


class PartitionFilter(TenancyFilterSet, CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tag = TagFilter()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = Partition
        fields = ['name', 'enforce_unique']


class LineFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    tag = TagFilter()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )
