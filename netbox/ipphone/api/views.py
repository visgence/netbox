from django.conf import settings
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from extras.api.views import CustomFieldModelViewSet
from ipphone import filters
from ipphone.models import Extension, Partition, Line
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
        (Line, ['name'], ['extension'], ['device'])
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

