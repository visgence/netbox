from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from extras.api.views import CustomFieldModelViewSet
from ipphone import filters
from ipphone.models import Extension, Partition
from utilities.api import FieldChoicesViewSet, ModelViewSet
from utilities.utils import get_subquery
from . import serializers

#
# Field choices
#

class IPPHONEFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Extension, ['dn'], ['partition']),
        (Partition, ['name'], ['enforce_unique']),
    )


#
# Extensions
#

class ExtensionViewSet(CustomFieldModelViewSet):
    queryset = Extension.objects.prefetch_related(
        'interface__device__device_type', 'tags'
    )
    serializer_class = serializers.ExtensionSerializer
    filterset_class = filters.ExtensionFilter

#
# Partitions
#

class PartitionViewSet(CustomFieldModelViewSet):
    queryset = Partition.objects.all()
    serializer_class = serializers.PartitionSerializer
    filterset_class = filters.PartitionFilter