from rest_framework import serializers

from ipphone.models import Extension, Partition, Line
from utilities.api import WritableNestedSerializer
from dcim.api.nested_serializers import NestedDeviceSerializer

__all__ = [
    'NestedExtensionSerializer',
    'NestedLineSerializer',
]


class NestedExtensionSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipphone-api:extension-detail')

    class Meta:
        model = Extension
        fields = ['id', 'partition', 'dn', 'url']


class NestedLineSerializer(WritableNestedSerializer):
    device = NestedDeviceSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='ipphone-api:line-detail')

    class Meta:
        model = Line
        fields = ['id', 'name', 'description', 'device', 'url']