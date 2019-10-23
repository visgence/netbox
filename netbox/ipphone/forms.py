from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.forms import TagField

from dcim.models import Site, Rack, Device
from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from utilities.forms import (
    add_blank_choice, APISelect, APISelectMultiple, BootstrapMixin, BulkEditNullBooleanSelect, ChainedModelChoiceField,
    CSVChoiceField, ExpandableExtensionField, FilterChoiceField, FlexibleModelChoiceField, ReturnURLForm, SlugField,
    StaticSelect2, StaticSelect2Multiple, BOOLEAN_WITH_BLANK_CHOICES, ComponentForm, ExpandableNameField
)
from .constants import EXTENSION_STATUS_CHOICES
from .models import Extension, Partition, Line


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
    line = forms.ModelChoiceField(
        queryset=Line.objects.all(),
        required=False
    )
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    tags = TagField(
        required=False
    )
    class Meta:
        model = Extension
        fields = [
            'dn', 'partition', 'status', 'description', 'device', 'tags', 'line',
        ]
        widgets = {
            'status': StaticSelect2()
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()

        if instance and instance.dn is not None:
            initial['dn'] = instance.dn
        else:
            initial['dn'] = ''

        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

        self.fields['partition'].empty_label = 'Global'

        if self.initial and 'line' in self.initial:
            self.fields['line'].queryset = Line.objects.filter(
                pk=self.initial['line']
            )
        elif 'line' not in self.initial:
            try:
                l = dict(args)
                if 'line' in l:
                    self.fields['line'].queryset = Line.objects.filter(
                        pk=args['line']
                    )
                else:
                    self.fields.pop('line')
            except Exception as e:
                print(e)
        else:
            self.fields.pop('line')

        if self.initial and 'device' in self.initial:
            self.fields['device'].queryset = Device.objects.filter(
                pk=self.initial['device']
            )
        else:
            self.fields['device'].choices = []


    def save(self, *args, **kwargs):
        extension = super().save(*args, **kwargs)
        if 'line' in self.data:
            line = self.data['line']
            Line.objects.filter(pk=line).update(extension=extension)

        return extension


class ExtensionBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableExtensionField(
        label='DN pattern'
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

    def save(self, *args, **kwargs):
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


#
# Lines
#

class LineForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = Line
        fields = [
            'device', 'name', 'description', 'extension'
        ]
        widgets = {
            'device': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class LineCreateForm(ComponentForm, forms.Form):
    name_pattern = ExpandableNameField(
        label='Name'
    )
    tags = TagField(
        required=False
    )

    def __init__(self, *args, **kwargs):

        kwargs['initial'] = kwargs.get('initial', {}).copy()
        kwargs['initial'].update({'enabled': True})

        super().__init__(*args, **kwargs)


 