from collections import OrderedDict

from django.conf import settings
from django.db.models import Count, F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from circuits.models import Circuit
from extras.api.views import CustomFieldModelViewSet
from ipam.models import Prefix, VLAN
from utilities.api import (
    get_serializer_for_model, IsAuthenticatedOrLoginNotRequired, FieldChoicesViewSet, ModelViewSet, ServiceUnavailable,
)
from utilities.utils import get_subquery
from virtualization.models import VirtualMachine
from . import serializers

from ipphone import filters
from ipphone.models import Extension, Partition, Line

#
# Field choices
#

class IPPHONEFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (Extension, ['status']),
        # (Partition, ['name', 'enforce_unique']),
        # (Line, ['name', 'extension', 'device'])
    )


#
# Extensions
#

class ExtensionViewSet(CustomFieldModelViewSet):
    queryset = Extension.objects.prefetch_related(
        'line__device__device_type', 'tags'
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


#
# Lines
#

class LineViewSet(ModelViewSet):
    queryset = Line.objects.prefetch_related(
        'device', 'extension', 'tags'
    )
    serializer_class = serializers.LineSerializer
    filterset_class = filters.LineFilter

    # @action(detail=True)
    # def graphs(self, request, pk):
    #     """
    #     A convenience method for rendering graphs for a particular interface.
    #     """
    #     interface = get_object_or_404(Interface, pk=pk)
    #     queryset = Graph.objects.filter(type=GRAPH_TYPE_INTERFACE)
    #     serializer = RenderedGraphSerializer(queryset, many=True, context={'graphed_object': interface})
    #     return Response(serializer.data)

