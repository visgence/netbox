from rest_framework import serializers

from ipphone.models import Phone
from utilities.api import WritableNestedSerializer

__all__ = [
    'NestedPhoneSerializer',
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


class NestedPhoneSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipphone-api:phone-detail')

    class Meta:
        model = Phone
        fields = ['id', 'ipphonepartition', 'phone_number']
