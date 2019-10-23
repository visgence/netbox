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
    url = serializers.SerializerMethodField() 
    class Meta:
        model = Extension
        fields = [
            'id', 'dn', 'description', 'url'
        ]

    def get_url(self, obj):
        url_name = 'ipphone-api:extension-detail'
        return reverse(url_name, kwargs={'pk': obj.pk}, request=self.context['request'])


class ExtensionSerializer(TaggitSerializer, CustomFieldModelSerializer):
    url = serializers.SerializerMethodField()
    status = ChoiceField(choices=EXTENSION_STATUS_CHOICES)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Extension
        fields = [
            'id', 'partition', 'dn', 'status', 'description', 'tags', 'custom_fields', 'created', 'last_updated', 'url'
        ]

    def get_url(self, obj):
        url_name = 'ipphone-api:extension-detail'
        return reverse(url_name, kwargs={'pk': obj.pk}, request=self.context['request'])


class LineSerializer(TaggitSerializer, CustomFieldModelSerializer):
    extension = ExtensionLineSerializer(required=False, allow_null=True)
    url = serializers.HyperlinkedIdentityField(view_name='ipphone-api:line-detail')

    class Meta:
        model = Line
        fields = ['id', 'name', 'extension', 'description', 'device', 'url']
