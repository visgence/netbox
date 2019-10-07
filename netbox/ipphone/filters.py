import django_filters
import netaddr
from django.core.exceptions import ValidationError
from django.db.models import Q
from netaddr.core import AddrFormatError

from dcim.models import Site, Device, Interface
from extras.filters import CustomFieldFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import NameSlugSearchFilterSet, NumericInFilter, TagFilter
from .constants import PHONE_STATUS_CHOICES
from .models import Phone, IPPhonePartition

class PhoneFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    parent = django_filters.CharFilter(
        method='search_by_parent',
        label='Parent prefix',
    )
    phone_number = django_filters.CharFilter(
        method='filter_phone_number',
        label='PhoneNumber',
    )
    ipphonepartition_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPPhonePartition.objects.all(),
        label='IPPhonePartition',
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__name',
        queryset=Interface.objects.all(),
        to_field_name='name',
        label='Interface (ID)',
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        label='Interface (ID)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PHONE_STATUS_CHOICES,
        null_value=None
    )
    tag = TagFilter()

    class Meta:
        model = Phone
        fields = ['phone_number', 'ipphonepartition']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(description__icontains=value) |
            Q(phone_number__istartswith=value)
        )
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(value.strip())
            return queryset.filter(phone_number_contained=query)
        except (AddrFormatError, ValueError):
            return queryset.none()


class IPPhonePartitionFilter(TenancyFilterSet, CustomFieldFilterSet):
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
        model = IPPhonePartition
        fields = ['name', 'enforce_unique']