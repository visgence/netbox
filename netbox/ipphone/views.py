from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django_tables2 import RequestConfig

from dcim.models import Device, Interface
from utilities.paginator import EnhancedPaginator
from utilities.views import (
    BulkCreateView, BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from virtualization.models import VirtualMachine
from . import filters, forms, tables
from .constants import *
from .models import Extension, Partition


#
# Partitions
#

class PartitionListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'ipphone.view_partition'
    queryset = Partition.objects.all()
    filter = filters.PartitionFilter
    filter_form = forms.PartitionFilterForm
    table = tables.PartitionTable
    template_name = 'ipphone/partition_list.html'


class PartitionView(PermissionRequiredMixin, View):
    permission_required = 'ipphone.view_partition'

    def get(self, request, pk):

        partition = get_object_or_404(Partition.objects.all(), pk=pk)

        return render(request, 'ipphone/partition.html', {
            'partition': partition
        })


class PartitionCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipphone.add_partition'
    model = Partition
    model_form = forms.PartitionForm
    template_name = 'ipphone/partition_edit.html'
    default_return_url = 'ipphone:partition_list'


class PartitionEditView(PartitionCreateView):
    permission_required = 'ipphone.change_partition'


class PartitionDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipphone.delete_partition'
    model = Partition
    default_return_url = 'ipphone:partition_list'


class PartitionBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipphone.add_partition'
    model_form = forms.PartitionCSVForm
    table = tables.PartitionTable
    default_return_url = 'ipphone:partition_list'


class PartitionBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipphone.change_partition'
    queryset = Partition.objects.all()
    filter = filters.PartitionFilter
    table = tables.PartitionTable
    form = forms.PartitionBulkEditForm
    default_return_url = 'ipphone:partition_list'


class PartitionBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
        permission_required = 'ipphone.delete_partition'
        queryset = Partition.objects.all()
        filter = filters.PartitionFilter
        table = tables.PartitionTable
        default_return_url = 'ipphone:partition_list'


#
# Extensions
#

class ExtensionListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'ipphone.view_dn'
    queryset = Extension.objects.prefetch_related(
        'interface__device'
    )
    filter = filters.ExtensionFilter
    filter_form = forms.ExtensionFilterForm
    table = tables.ExtensionDetailTable
    template_name = 'ipphone/extension_list.html'


class ExtensionView(PermissionRequiredMixin, View):
    permission_required = 'ipphone.view_extension'

    def get(self, request, pk):

        extension = get_object_or_404(Extension.objects.prefetch_related('interface__device'), pk=pk)

        return render(request, 'ipphone/extension.html', {
            'extension': extension,
        })


class ExtensionCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipphone.add_extension'
    model = Extension
    model_form = forms.ExtensionForm
    template_name = 'ipphone/extension_edit.html'
    default_return_url = 'ipphone:extension_list'

    def alter_obj(self, obj, request, url_args, url_kwargs):

        interface_id = request.GET.get('interface')
        if interface_id:
            try:
                obj.interface = Interface.objects.get(pk=interface_id)
            except (ValueError, Interface.DoesNotExist):
                pass

        return obj


class ExtensionEditView(ExtensionCreateView):
    permission_required = 'ipphone.change_extension'


class ExtensionAssignView(PermissionRequiredMixin, View):
    """
    Search for Extension Numbers to be assigned to an Interface.
    """
    permission_required = 'ipphone.change_extension'

    def dispatch(self, request, *args, **kwargs):

        # Redirect user if an interface has not been provided
        if 'interface' not in request.GET:
            return redirect('ipphone:extension_add')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        form = forms.ExtensionAssignForm()

        return render(request, 'ipphone/extension_assign.html', {
            'form': form,
            'return_url': request.GET.get('return_url', ''),
        })

    def post(self, request):

        form = forms.ExtensionAssignForm(request.POST)
        table = None

        if form.is_valid():

            queryset = Extension.objects.prefetch_related(
                'interface__device'
            ).filter(
                dn__istartswith=form.cleaned_data['dn'],
            )[:100]  # Limit to 100 results
            table = tables.ExtensionAssignTable(queryset)

        return render(request, 'ipphone/extension_assign.html', {
            'form': form,
            'table': table,
            'return_url': request.GET.get('return_url', ''),
        })


class ExtensionDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipphone.delete_extension'
    model = Extension
    default_return_url = 'ipphone:extension_list'


class ExtensionBulkCreateView(PermissionRequiredMixin, BulkCreateView):
    permission_required = 'ipphone.add_extension'
    form = forms.ExtensionBulkCreateForm
    model_form = forms.ExtensionBulkAddForm
    pattern_target = 'dn'
    template_name = 'ipphone/extension_bulk_add.html'
    default_return_url = 'ipphone:extension_list'


class ExtensionBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipphone.add_extension'
    # queryset = Extension.objects.all()
    model_form = forms.ExtensionCSVForm
    table = tables.ExtensionTable
    default_return_url = 'ipphone:extension_list'


class ExtensionBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipphone.change_extension'
    queryset = Extension.objects.prefetch_related('interface__device')
    filter = filters.ExtensionFilter
    table = tables.ExtensionTable
    form = forms.ExtensionBulkEditForm
    default_return_url = 'ipphone:extension_list'


class ExtensionBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipphone.delete_extension'
    queryset = Extension.objects.prefetch_related('interface__device')
    filter = filters.ExtensionFilter
    table = tables.ExtensionTable
    default_return_url = 'ipphone:extension_list'


