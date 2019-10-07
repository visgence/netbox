from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.nested_serializers import NestedDeviceSerializer, NestedSiteSerializer
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipphone.constants import *
from ipphone.models import Extension, Partition
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

class ExtensionInterfaceSerializer(WritableNestedSerializer):
    url = serializers.SerializerMethodField() 
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = Interface
        fields = [
            'id', 'url', 'device', 'name',
        ]

    def get_url(self, obj):
        url_name = 'dcim-api:interface-detail'
        return reverse(url_name, kwargs={'pk': obj.pk}, request=self.context['request'])


class ExtensionSerializer(TaggitSerializer, CustomFieldModelSerializer):
    status = ChoiceField(choices=EXTENSION_STATUS_CHOICES, required=False)
    interface = ExtensionInterfaceSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Extension
        fields = [
            'id', 'partition', 'dn', 'status', 'interface', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
        ]

