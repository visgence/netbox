from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.forms import TagField

from dcim.models import Site, Rack, Device, Interface
from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from utilities.forms import (
    add_blank_choice, APISelect, APISelectMultiple, BootstrapMixin, BulkEditNullBooleanSelect, ChainedModelChoiceField,
    CSVChoiceField, ExpandableExtensionField, FilterChoiceField, FlexibleModelChoiceField, ReturnURLForm, SlugField,
    StaticSelect2, StaticSelect2Multiple, BOOLEAN_WITH_BLANK_CHOICES
)
from virtualization.models import VirtualMachine
from .constants import EXTENSION_STATUS_CHOICES
from .models import Extension, Partition


#
# Partitions
#

class PartitionForm(BootstrapMixin, CustomFieldForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = Partition
        fields = [
            'name', 'enforce_unique', 'description', 'tags',
        ]


class PartitionCSVForm(forms.ModelForm):
    class Meta:
        model = Partition
        fields = Partition.csv_headers
        help_texts = {
            'name': 'Partition name',
        }


class PartitionBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Partition.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    enforce_unique = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
        label='Enforce unique space'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    class Meta:
        nullable_fields = [
            'description',
        ]


class PartitionFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Partition
    field_order = ['q']
    q = forms.CharField(
        required=False,
        label='Search'
    )


#
# Extension
#

class ExtensionForm(BootstrapMixin, ReturnURLForm, CustomFieldForm):
    interface = forms.ModelChoiceField(
        queryset=Interface.objects.all(),
        required=False
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site',
        widget=APISelect(
            api_url="/api/dcim/sites/",
			filter_for={
                'device': 'site_id'
            }
        )
    )
    device = ChainedModelChoiceField(
        queryset=Device.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        label='Device',
        widget=APISelect(
            api_url='/api/dcim/devices/',
            display_field='display_name',
            filter_for={
                'dn': 'device_id'
            }
        )
    )
    tags = TagField(
        required=False
    )

    class Meta:
        model = Extension
        fields = [
            'dn', 'partition', 'status', 'description', 'interface', 'site', 'tags',
        ]
        widgets = {
            'status': StaticSelect2()
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance and instance.dn is not None:
            initial['dn'] = instance.dn
        else:
            initial['dn'] = ''
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        self.fields['partition'].empty_label = 'Global'

        # Limit interface selections to those belonging to the parent device/VM
        if self.instance and self.instance.interface:
            self.fields['interface'].queryset = Interface.objects.filter(
                device=self.instance.interface.device
            )
        else:
            self.fields['interface'].choices = []

        if self.instance.pk and self.instance.interface is not None:
            parent = self.instance.interface.parent

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):

        extension = super().save(*args, **kwargs)

        # Assign/clear this Extension as the primary for the associated Device.
        if self.cleaned_data['interface']:
            parent = self.cleaned_data['interface'].parent
            parent.save()


        return extension


class ExtensionBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableExtensionField(
        label='Extension pattern'
    )


class ExtensionBulkAddForm(BootstrapMixin, CustomFieldForm):

    class Meta:
        model = Extension
        fields = [
            'dn', 'partition', 'status', 'description'
        ]
        widgets = {
            'partition': APISelect(
                api_url="/api/ipphone/partitions/"
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ExtensionCSVForm(forms.ModelForm):

    status = CSVChoiceField(
        choices=EXTENSION_STATUS_CHOICES,
        help_text='Operational status'
    )
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name or ID of assigned device',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    interface_name = forms.CharField(
        help_text='Name of assigned interface',
        required=False
    )
    partition = FlexibleModelChoiceField(
        queryset=Partition.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Parent Partition (or {ID})',
        error_messages={
            'invalid_choice': 'Partition not found.',
        }
    )


    class Meta:
        model = Extension
        fields = Extension.csv_headers

    def clean(self):
        super().clean()

        device = self.cleaned_data.get('device')
        interface_name = self.cleaned_data.get('interface_name')

        # Validate interface
        if interface_name and device:
            try:
                self.instance.interface = Interface.objects.get(device=device, name=interface_name)
            except Interface.DoesNotExist:
                raise forms.ValidationError("Invalid interface {} for device {}".format(
                    interface_name, device
                ))
        elif interface_name:
            raise forms.ValidationError("Interface given ({}) but parent device not specified".format(
                interface_name
            ))
        elif device:
            raise forms.ValidationError("Device specified ({}) but interface missing".format(device))

    def save(self, *args, **kwargs):

        # Set interface
        if self.cleaned_data['device'] and self.cleaned_data['interface_name']:
            self.instance.interface = Interface.objects.get(
                device=self.cleaned_data['device'],
                name=self.cleaned_data['interface_name']
            )

        dn = super().save(*args, **kwargs)

        return dn


class ExtensionBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Extension.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(EXTENSION_STATUS_CHOICES),
        required=False,
        widget=StaticSelect2()
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'description',
        ]


class ExtensionAssignForm(BootstrapMixin, forms.Form):
    dn = forms.CharField(
        label='DN'
    )


class ExtensionFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Extension
    field_order = [
        'q', 'partition_id', 'status'
    ]
    q = forms.CharField(
        required=False,
        label='Search'
    )
    partition_id = FilterChoiceField(
        queryset=Partition.objects.all(),
        label='Partition',
        null_label='-- Global --',
        widget=APISelectMultiple(
            api_url="/api/ipphone/partitions/",
            null_option=True,
        )
    )
    status = forms.MultipleChoiceField(
        choices=EXTENSION_STATUS_CHOICES,
        required=False,
        widget=StaticSelect2Multiple()
    )

