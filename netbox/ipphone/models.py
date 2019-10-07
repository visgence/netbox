import netaddr
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.expressions import RawSQL
from django.urls import reverse
from taggit.managers import TaggableManager

from dcim.models import Interface
from extras.models import CustomFieldModel, ObjectChange, TaggedItem
from utilities.models import ChangeLoggedModel
from utilities.utils import serialize_object
from .constants import *


class PhoneManager(models.Manager):

    def search(self):
        return Phone.objects.all()


class Phone(ChangeLoggedModel, CustomFieldModel):

    phone_number = models.CharField(
        max_length=25,
        help_text='Phone number 555-555-5555'
    )
    ipphonepartition = models.ForeignKey(
        to='ipphone.IPPhonePartition',
        on_delete=models.PROTECT,
        # related_name='',
        blank=True,
        null=True,
        verbose_name='IP Phone Partition'
    )
    status = models.PositiveSmallIntegerField(
        choices=PHONE_STATUS_CHOICES,
        default=PHONE_STATUS_ACTIVE,
        verbose_name='Status',
        help_text='The operational status of this Phone Number'
    )
    interface = models.ForeignKey(
        to='dcim.Interface',
        on_delete=models.CASCADE,
        related_name='phone',
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    objects = PhoneManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'phone_number', 'ipphonepartition', 'status', 'device', 'interface_name', 'description',
    ]

    class Meta:
        ordering = ['id', 'phone_number', 'ipphonepartition']
        verbose_name = 'Phone Number'
        verbose_name_plural = 'Phone Numbers'

    def __str__(self):
        return str(self.phone_number)

    def get_absolute_url(self):
        return reverse('ipphone:phone', args=[self.pk])

    def get_duplicates(self):
        return Phone.objects.filter(phone_number=self.phone_number).exclude(pk=self.pk)

    def clean(self):

        if self.phone_number:

            # Enforce unique Phone (if applicable)
            if self.ipphonepartition and self.ipphonepartition.enforce_unique:
                duplicate_pns = self.get_duplicates()
                if duplicate_pns:
                    raise ValidationError({
                        'phone_number': "Duplicate Phone Number found in {}: {}".format(
                            "IP Phone Partition {}".format(self.ipphonepartition) if self.ipphonepartition else "global table",
                            duplicate_pns.first(),
                        )
                    })

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def to_objectchange(self, action):
        # Annotate the assigned Interface (if any)
        try:
            parent_obj = self.interface
        except ObjectDoesNotExist:
            parent_obj = None

        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=parent_obj,
            object_data=serialize_object(self)
        )

    def to_csv(self):
        return (
            self.phone_number,
            self.get_status_display(),
            self.device.identifier if self.device else None,
            self.interface.name if self.interface else None,
            self.description,
            self.ipphonepartition,
        )

    @property
    def device(self):
        if self.interface:
            return self.interface.device
        return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]


class IPPhonePartitionManager(models.Manager):

    def search(self):
        return IPPhonePartition.objects.all()


class IPPhonePartition(ChangeLoggedModel, CustomFieldModel):
    name = models.CharField(
        max_length=50
    )
    enforce_unique = models.BooleanField(
        default=True,
        verbose_name='Enforce unique space',
        help_text='Prevent duplicate extensions within this IP Phone Partition'
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager(through=TaggedItem)

    csv_headers = ['name', 'enforce_unique', 'description']

    class Meta:
        ordering = ['name']
        verbose_name = 'IP Phone Partition'
        verbose_name_plural = 'IP Phone Partitions'

    def __str__(self):
        return self.display_name or super().__str__()

    def get_absolute_url(self):
        return reverse('ipphone:ipphonepartitions', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.enforce_unique,
            self.description,
        )

    @property
    def display_name(self):
        return self.name
