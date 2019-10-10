from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.nested_serializers import NestedDeviceSerializer, NestedSiteSerializer
from extras.api.customfields import CustomFieldModelSerializer
from ipphone.constants import *
from ipphone.models import Extension, Partition, Line
from utilities.api import (
    ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer, WritableNestedSerializer,
)
from virtualization.api.nested_serializers import NestedVirtualMachineSerializer
from .nested_serializers import *

#
# Partitions
#

class PartitionSerializer(TaggitSerializer, CustomFieldModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Partition
        fields = [
            'id', 'name', 'enforce_unique', 'description', 'tags', 'custom_fields',
        ]


#
# Extensions
#

class ExtensionLineSerializer(WritableNestedSerializer):
    # url = serializers.SerializerMethodField() 
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = Line
        fields = [
            'id', 'device', 'name',
        ]

    def get_url(self, obj):
        url_name = 'ipphone-api:line-detail'
        return reverse(url_name, kwargs={'pk': obj.pk}, request=self.context['request'])


class ExtensionSerializer(TaggitSerializer, CustomFieldModelSerializer):
    status = ChoiceField(choices=EXTENSION_STATUS_CHOICES, required=False)
    line = ExtensionLineSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Extension
        fields = [
            'id', 'partition', 'dn', 'status', 'line', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


class LineSerializer(TaggitSerializer):
    device = NestedDeviceSerializer()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Line
        fields = [
            'id', 'device', 'name',  'tags', 'count_extensions',
        ]

    # TODO: This validation should be handled by Line.clean()
    def validate(self, data):

        # All associated VLANs be global or assigned to the parent device's site.
        device = self.line.device if self.line else data.get('device')
        