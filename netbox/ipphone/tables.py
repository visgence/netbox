import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Interface
from tenancy.tables import COL_TENANT
from utilities.tables import BaseTable, BooleanColumn, ToggleColumn
from .models import Phone, IPPhonePartition

IPPHONEPARTITION_LINK = """
{% if record.ipphonepartition %}
    <a href="{{ record.ipphonepartition.get_absolute_url }}">{{ record.ipphonepartition }}</a>
{% else %}
    Global
{% endif %}
"""

PHONE_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.phone_number }}</a>
{% elif perms.ipphone.add_phone %}
    <a href="{% url 'ipphone:phone_add' %}?phone_number={{ record.1 }}" class="btn btn-xs btn-success">{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} PN{{ record.0|pluralize }} available
{% endif %}
"""

PHONE_ASSIGN_LINK = """
<a href="{% url 'ipphone:phone_edit' pk=record.pk %}?interface={{ request.GET.interface }}&return_url={{ request.GET.return_url }}">{{ record }}</a>
"""

PHONE_PARENT = """
{% if record.interface %}
    <a href="{{ record.interface.parent.get_absolute_url }}">{{ record.interface.parent }}</a>
{% else %}
    &mdash;
{% endif %}
"""

STATUS_LABEL = """
{% if record.pk %}
    <span class="label label-{{ record.get_status_class }}">{{ record.get_status_display }}</span>
{% else %}
    <span class="label label-success">Available</span>
{% endif %}
"""

#
# Phones
#

class PhoneTable(BaseTable):
    pk = ToggleColumn()
    phone_number = tables.TemplateColumn(PHONE_LINK, verbose_name='Phone Number')
    ipphonepartition = tables.TemplateColumn(IPPHONEPARTITION_LINK, verbose_name='IP Phone Partition')
    status = tables.TemplateColumn(STATUS_LABEL)
    parent = tables.TemplateColumn(PHONE_PARENT, orderable=False)
    interface = tables.Column(orderable=False)

    class Meta(BaseTable.Meta):
        model = Phone
        fields = (
            'pk', 'phone_number', 'ipphonepartition', 'status', 'parent', 'interface', 'description',
        )


class PhoneDetailTable(PhoneTable):
    class Meta(PhoneTable.Meta):
        fields = (
            'pk', 'phone_number', 'ipphonepartition', 'status', 'parent', 'interface', 'description',
        )


class PhoneAssignTable(BaseTable):
    phone_number = tables.TemplateColumn(PHONE_ASSIGN_LINK, verbose_name='Phone Number')
    status = tables.TemplateColumn(STATUS_LABEL)
    parent = tables.TemplateColumn(PHONE_PARENT, orderable=False)
    interface = tables.Column(orderable=False)

    class Meta(BaseTable.Meta):
        model = Phone
        fields = ('phone_number', 'ipphonepartition', 'status', 'parent', 'interface', 'description')
        orderable = False


class InterfacePhoneTable(BaseTable):
    """
    List Phone Number assigned to a specific Interface.
    """
    phone_number = tables.TemplateColumn(PHONE_ASSIGN_LINK, verbose_name='Phone Number')
    status = tables.TemplateColumn(STATUS_LABEL)

    class Meta(BaseTable.Meta):
        model = Phone
        fields = ('phone_number', 'ipphonepartition', 'status', 'description')


#
# IPPhonePartitions
#

class IPPhonePartitionTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = IPPhonePartition
        fields = ('pk', 'name', 'description', 'enforce_unique')

