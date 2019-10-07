from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.forms import TagField

from dcim.models import Site, Rack, Device, Interface
from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from utilities.forms import (
    add_blank_choice, APISelect, APISelectMultiple, BootstrapMixin, BulkEditNullBooleanSelect, ChainedModelChoiceField,
    CSVChoiceField, ExpandableIPAddressField, FilterChoiceField, FlexibleModelChoiceField, ReturnURLForm, SlugField,
    StaticSelect2, StaticSelect2Multiple, BOOLEAN_WITH_BLANK_CHOICES
)
from virtualization.models import VirtualMachine
from .constants import PHONE_STATUS_CHOICES
from .models import Phone, IPPhonePartition


#
# IPPhonePartitions
#

class IPPhonePartitionForm(BootstrapMixin, CustomFieldForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = IPPhonePartition
        fields = [
            'name', 'enforce_unique', 'description', 'tags',
        ]


class IPPhonePartitionCSVForm(forms.ModelForm):
    class Meta:
        model = IPPhonePartition
        fields = IPPhonePartition.csv_headers
        help_texts = {
            'name': 'IP Phone Partition name',
        }


class IPPhonePartitionBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=IPPhonePartition.objects.all(),
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


class IPPhonePartitionFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = IPPhonePartition
    field_order = ['q']
    q = forms.CharField(
        required=False,
        label='Search'
    )


#
# Phone
#

class PhoneForm(BootstrapMixin, ReturnURLForm, CustomFieldForm):
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
                'phone_number': 'device_id'
            }
        )
    )
    # phone_number = ChainedModelChoiceField(
    #     queryset=Phone.objects.all(),
    #     chains=(
    #         ('interface__device', 'device'),
    #     ),
    #     required=False,
    #     label='Phone Number',
    #     widget=APISelect(
    #         api_url='/api/ipphone/phones/',
    #         display_field='phone_number'
    #     )
    # )
    tags = TagField(
        required=False
    )

    class Meta:
        model = Phone
        fields = [
            'phone_number', 'ipphonepartition', 'status', 'description', 'interface', 'site', 'tags',
        ]
        widgets = {
            'status': StaticSelect2()
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance and instance.phone_number is not None:
            initial['phone_number'] = instance.phone_number
        else:
            initial['phone_number'] = ''
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)


        # Limit interface selections to those belonging to the parent device/VM
        if self.instance and self.instance.interface:
            self.fields['interface'].queryset = Interface.objects.filter(
                device=self.instance.interface.device
            )
        else:
            self.fields['interface'].choices = []

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):

        phone = super().save(*args, **kwargs)

        # Assign/clear this Phone Number as the primary for the associated Device.
        # parent = self.cleaned_data['interface'].parent
        phone.save()

        return phone


class PhoneBulkCreateForm(BootstrapMixin, forms.Form):
    # pattern = ExpandablePhoneField(
    #     label='Phone pattern'
    # )
    pattern = ''


class PhoneBulkAddForm(BootstrapMixin, CustomFieldForm):

    class Meta:
        model = Phone
        fields = [
            'phone_number', 'ipphonepartition', 'status', 'description'
        ]
        widgets = {
            'ipphonepartition': APISelect(
                api_url="/api/ipphone/ipphonepartitions/"
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PhoneCSVForm(forms.ModelForm):

    status = CSVChoiceField(
        choices=PHONE_STATUS_CHOICES,
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
    ipphonepartition = FlexibleModelChoiceField(
        queryset=IPPhonePartition.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Parent IP Phone Partition (or {ID})',
        error_messages={
            'invalid_choice': 'IP Phone Partition not found.',
        }
    )


    class Meta:
        model = Phone
        fields = Phone.csv_headers

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

        phone_number = super().save(*args, **kwargs)
        phone_number.save()
        # parent = self.cleaned_data['device']
        # parent.save()

        return phone_number


class PhoneBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Phone.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(PHONE_STATUS_CHOICES),
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


class PhoneAssignForm(BootstrapMixin, forms.Form):
    phone_number = forms.CharField(
        label='Phone Number'
    )


class PhoneFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Phone
    field_order = [
        'q', 'parent', 'ipphonepartition', 'status'
    ]
    q = forms.CharField(
        required=False,
        label='Search'
    )
    # parent = forms.CharField(
    #     required=False,
    #     widget=forms.TextInput(
    #         attrs={
    #             'placeholder': 'Prefix',
    #         }
    #     ),
    #     label='Parent Prefix'
    # )
    status = forms.MultipleChoiceField(
        choices=PHONE_STATUS_CHOICES,
        required=False,
        widget=StaticSelect2Multiple()
    )

