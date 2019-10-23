import django_tables2 as tables
from django_tables2.utils import Accessor

from tenancy.tables import COL_TENANT
from utilities.tables import BaseTable, BooleanColumn, ToggleColumn
from .models import Extension, Partition, Line

PARTITION_LINK = """
{% if record.partition %}
    <a href="{{ record.partition.get_absolute_url }}">{{ record.partition }}</a>
{% else %}
    Global
{% endif %}
"""

EXTENSION_LINK = """
{% if record.pk %}
    <a href="{{ record.get_absolute_url }}">{{ record.dn }}</a>
{% elif perms.ipphone.add_extension %}
    <a href="{% url 'ipphone:extension_add' %}?dn={{ record.1 }}" class="btn btn-xs btn-success">{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} PN{{ record.0|pluralize }} available
{% endif %}
"""

EXTENSION_ASSIGN_LINK = """
<a href="{% url 'ipphone:extension_edit' pk=record.pk %}">{{ record }}</a>
"""

EXTENSION_ASSIGN_LINK2 = """
<a href="{% url 'ipphone:extension_edit' pk=record.pk %}?line={{ request.GET.line }}&return_url={{ request.GET.return_url }}">{{ record }}</a>
"""


EXTENSION_PARENT = """
{% if record.line %}
    <a href="{{ record.line.parent.get_absolute_url }}">{{ record.line }}</a>
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
# Extensions
#

class ExtensionTable(BaseTable):
    pk = ToggleColumn()
    dn = tables.TemplateColumn(EXTENSION_LINK, verbose_name='DN')
    partition = tables.TemplateColumn(PARTITION_LINK, verbose_name='Partition')
    status = tables.TemplateColumn(STATUS_LABEL)

    class Meta(BaseTable.Meta):
        model = Extension
        fields = (
            'pk', 'dn', 'partition', 'status', 'description',
        )


class ExtensionDetailTable(ExtensionTable):
    class Meta(ExtensionTable.Meta):
        fields = (
            'pk', 'dn', 'partition', 'status', 'description',
        )


class ExtensionAssignTable(BaseTable):
    dn = tables.TemplateColumn(EXTENSION_ASSIGN_LINK2, verbose_name='DN')
    status = tables.TemplateColumn(STATUS_LABEL)

    class Meta(BaseTable.Meta):
        model = Extension
        fields = ('dn', 'partition', 'status', 'description')
        orderable = False


#
# Partitions
#

class PartitionTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()

    class Meta(BaseTable.Meta):
        model = Partition
        fields = ('pk', 'name', 'description', 'enforce_unique')


#
# Lines
#

class LineTable(BaseTable):

    class Meta(BaseTable.Meta):
        model = Line
        fields = ('name', 'description', 'extension')


class LineExtensionTable(BaseTable):
    """
    List Extensions assigned to a specific Line.
    """
    extension = tables.TemplateColumn(EXTENSION_ASSIGN_LINK, verbose_name='Extension')
    partition = tables.TemplateColumn(PARTITION_LINK, verbose_name='Partition')

    class Meta(BaseTable.Meta):
        model = Extension
        fields = ('extension', 'partition')