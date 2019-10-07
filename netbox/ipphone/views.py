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
from .models import Phone, IPPhonePartition


#
# IPPhonePartitions
#

class IPPhonePartitionListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'ipphone.view_ipphonepartition'
    queryset = IPPhonePartition.objects.all() # prefetch_related('tenant')
    filter = filters.IPPhonePartitionFilter
    filter_form = forms.IPPhonePartitionFilterForm
    table = tables.IPPhonePartitionTable
    template_name = 'ipphone/ipphonepartition_list.html'


class IPPhonePartitionView(PermissionRequiredMixin, View):
    permission_required = 'ipphone.view_ipphonepartition'

    def get(self, request, pk):

        ipphonepartition = get_object_or_404(IPPhonePartition.objects.all(), pk=pk)

        return render(request, 'ipphone/ipphonepartition.html', {
            'ipphonepartition': ipphonepartition
        })


class IPPhonePartitionCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipphone.add_ipphonepartition'
    model = IPPhonePartition
    model_form = forms.IPPhonePartitionForm
    template_name = 'ipphone/ipphonepartition_edit.html'
    default_return_url = 'ipphone:ipphonepartition_list'


class IPPhonePartitionEditView(IPPhonePartitionCreateView):
    permission_required = 'ipphone.change_ipphonepartition'


class IPPhonePartitionDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipphone.delete_ipphonepartition'
    model = IPPhonePartition
    default_return_url = 'ipphone:ipphonepartition_list'


class IPPhonePartitionBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipphone.add_ipphonepartition'
    model_form = forms.IPPhonePartitionCSVForm
    table = tables.IPPhonePartitionTable
    default_return_url = 'ipphone:ipphonepartition_list'


class IPPhonePartitionBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipphone.change_ipphonepartition'
    filter = filters.IPPhonePartitionFilter
    table = tables.IPPhonePartitionTable
    form = forms.IPPhonePartitionBulkEditForm
    default_return_url = 'ipphone:ipphonepartition_list'


class IPPhonePartitionBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
        permission_required = 'ipphone.delete_ipphonepartition'
        queryset = IPPhonePartition.objects.all() # prefetch_related('')
        filter = filters.IPPhonePartitionFilter
        table = tables.IPPhonePartitionTable
        default_return_url = 'ipphone:ipphonepartition_list'


#
# Phone Numbers
#

class PhoneListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'ipphone.view_phone_number'
    queryset = Phone.objects.prefetch_related(
        'interface__device'
    )
    filter = filters.PhoneFilter
    filter_form = forms.PhoneForm
    table = tables.PhoneDetailTable
    template_name = 'ipphone/phone_list.html'


class PhoneView(PermissionRequiredMixin, View):
    permission_required = 'ipphone.view_phone'

    def get(self, request, pk):

        phone = get_object_or_404(Phone.objects.prefetch_related('interface__device'), pk=pk)

        # # TBD 

        # # Duplicate Phone Numbers table
        # # duplicate_pns = Phone.objects.filter(
        # #     phone_number=str(phone.phone_number)
        # # ).exclude(
        # #     pk=phone.pk
        # # ).prefetch_related(
        # #     'interface__device'
        # # )
        # duplicate_pns = []

        # duplicate_pns_table = tables.PhoneTable(list(duplicate_pns), orderable=False)

        # related_pns = []

        # # related_pns = Phone.objects.prefetch_related(
        # #     'interface__device'
        # # ).exclude(
        # #     phone_number=str(phone.phone_number)
        # # )

        # related_pns_table = tables.PhoneTable(list(related_pns), orderable=False)

        return render(request, 'ipphone/phone.html', {
            'phone': phone,
            # 'duplicate_pns_table': duplicate_pns_table,
            # 'related_pns_table': related_pns_table,
        })


class PhoneCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'ipphone.add_phone'
    model = Phone
    model_form = forms.PhoneForm
    template_name = 'ipphone/phone_edit.html'
    default_return_url = 'ipphone:phone_list'

    def alter_obj(self, obj, request, url_args, url_kwargs):

        interface_id = request.GET.get('interface')
        if interface_id:
            try:
                obj.interface = Interface.objects.get(pk=interface_id)
            except (ValueError, Interface.DoesNotExist):
                pass

        return obj


class PhoneEditView(PhoneCreateView):
    permission_required = 'ipphone.change_phone'


class PhoneAssignView(PermissionRequiredMixin, View):
    """
    Search for Phone Numbers to be assigned to an Interface.
    """
    permission_required = 'ipphone.change_phone'

    def dispatch(self, request, *args, **kwargs):

        # Redirect user if an interface has not been provided
        if 'interface' not in request.GET:
            return redirect('ipphone:phone_add')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):

        form = forms.PhoneAssignForm()

        return render(request, 'ipphone/phone_assign.html', {
            'form': form,
            'return_url': request.GET.get('return_url', ''),
        })

    def post(self, request):

        form = forms.PhoneAssignForm(request.POST)
        table = None

        if form.is_valid():

            queryset = Phone.objects.prefetch_related(
                'interface__device'
            ).filter(
                phone_number__istartswith=form.cleaned_data['phone_number'],
            )[:100]  # Limit to 100 results
            table = tables.PhoneAssignTable(queryset)

        return render(request, 'ipphone/phone_assign.html', {
            'form': form,
            'table': table,
            'return_url': request.GET.get('return_url', ''),
        })


class PhoneDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'ipphone.delete_phone'
    model = Phone
    default_return_url = 'ipphone:phone_list'


class PhoneBulkCreateView(PermissionRequiredMixin, BulkCreateView):
    permission_required = 'ipphone.add_phone'
    form = forms.PhoneBulkCreateForm
    model_form = forms.PhoneBulkAddForm
    pattern_target = 'phone_number'
    template_name = 'ipphone/phone_bulk_add.html'
    default_return_url = 'ipphone:phone_list'


class PhoneBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'ipphone.add_phone'
    # queryset = Phone.objects.all()
    model_form = forms.PhoneCSVForm
    table = tables.PhoneTable
    default_return_url = 'ipphone:phone_list'


class PhoneBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'ipphone.change_phone'
    queryset = Phone.objects.prefetch_related('interface__device')
    filter = filters.PhoneFilter
    table = tables.PhoneTable
    form = forms.PhoneBulkEditForm
    default_return_url = 'ipphone:phone_list'


class PhoneBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'ipphone.delete_phone'
    queryset = Phone.objects.prefetch_related('interface__device')
    filter = filters.PhoneFilter
    table = tables.PhoneTable
    default_return_url = 'ipphone:phone_list'


