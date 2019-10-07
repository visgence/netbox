from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.nested_serializers import NestedDeviceSerializer, NestedSiteSerializer
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipphone.constants import *
from ipphone.models import Phone, IPPhonePartition
from utilities.api import (
    ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer, WritableNestedSerializer,
)
from virtualization.api.nested_serializers import NestedVirtualMachineSerializer
from .nested_serializers import *

#
# IPPhonePartitions
#

class IPPhonePartitionSerializer(TaggitSerializer, CustomFieldModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = IPPhonePartition
        fields = [
            'id', 'name', 'enforce_unique', 'description', 'tags', 'custom_fields',
        ]


#
# Phone Numbers
#

class PhoneInterfaceSerializer(WritableNestedSerializer):
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


class PhoneSerializer(TaggitSerializer, CustomFieldModelSerializer):
    status = ChoiceField(choices=PHONE_STATUS_CHOICES, required=False)
    interface = PhoneInterfaceSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Phone
        fields = [
            'id', 'ipphonepartition', 'phone_number', 'status', 'interface', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
        ]

