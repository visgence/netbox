from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from extras.api.views import CustomFieldModelViewSet
from ipphone import filters
from ipphone.models import Phone, IPPhonePartition
from utilities.api import FieldChoicesViewSet, ModelViewSet
from utilities.utils import get_subquery
from . import serializers

#
# Field choices
#

class IPPHONEFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Phone, ['phone_number'], ['ipphonepartition']),
        (IPPhonePartition, ['name'], ['enforce_unique']),
    )


#
# Phone Numbers
#

class PhoneViewSet(CustomFieldModelViewSet):
    queryset = Phone.objects.prefetch_related(
        'interface__device__device_type', 'tags'
    )
    serializer_class = serializers.PhoneSerializer
    filterset_class = filters.PhoneFilter

#
# IPPhonePartitions
#

class IPPhonePartitionViewSet(CustomFieldModelViewSet):
    queryset = IPPhonePartition.objects.all()
    serializer_class = serializers.IPPhonePartitionSerializer
    filterset_class = filters.IPPhonePartitionFilter