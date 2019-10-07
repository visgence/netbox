from rest_framework import serializers

from ipphone.models import Extension
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedExtensionSerializer',
    # 'NestedVRFSerializer',
]


#
# VRFs
#

# class NestedVRFSerializer(WritableNestedSerializer):
#     url = serializers.HyperlinkedIdentityField(view_name='ipphone-api:vrf-detail')
#     prefix_count = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = VRF
#         fields = ['id', 'url', 'name', 'rd', 'prefix_count']


#
# IP addresses
#


class NestedExtensionSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipphone-api:extension-detail')

    class Meta:
        model = Extension
        fields = ['id', 'partition', 'dn']
