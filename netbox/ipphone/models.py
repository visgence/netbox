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


class ExtensionManager(models.Manager):

    def search(self):
        return Extension.objects.all()


class Extension(ChangeLoggedModel, CustomFieldModel):

    dn = models.CharField(
        max_length=25,
        help_text='Extension'
    )
    partition = models.ForeignKey(
        to='ipphone.Partition',
        on_delete=models.PROTECT,
        # related_name='',
        blank=True,
        null=True,
        verbose_name='Partition'
    )
    status = models.PositiveSmallIntegerField(
        choices=EXTENSION_STATUS_CHOICES,
        default=EXTENSION_STATUS_ACTIVE,
        verbose_name='Status',
        help_text='The operational status of this DN'
    )
    interface = models.ForeignKey(
        to='dcim.Interface',
        on_delete=models.CASCADE,
        related_name='extension',
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

    objects = ExtensionManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'dn', 'partition', 'status', 'device', 'interface_name', 'description',
    ]

    class Meta:
        ordering = ['id', 'dn', 'partition']
        verbose_name = 'DN'
        verbose_name_plural = 'DNs'

    def __str__(self):
        return str(self.dn)

    def get_absolute_url(self):
        return reverse('ipphone:extension', args=[self.pk])

    def get_duplicates(self):
        return Extension.objects.filter(dn=self.dn).exclude(pk=self.pk)

    def clean(self):

        if self.dn:

            # Enforce unique DN (if applicable)
            if self.partition and self.partition.enforce_unique:
                duplicate_pns = self.get_duplicates()
                if duplicate_pns:
                    raise ValidationError({
                        'dn': "Duplicate DN found in {}: {}".format(
                            "Partition {}".format(self.partition) if self.partition else "global table",
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
            self.dn,
            self.get_status_display(),
            self.device.identifier if self.device else None,
            self.interface.name if self.interface else None,
            self.description,
            self.partition,
        )

    @property
    def device(self):
        if self.interface:
            return self.interface.device
        return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]


class PartitionManager(models.Manager):

    def search(self):
        return Partition.objects.all()


class Partition(ChangeLoggedModel, CustomFieldModel):
    name = models.CharField(
        max_length=50
    )
    enforce_unique = models.BooleanField(
        default=True,
        verbose_name='Enforce unique space',
        help_text='Prevent duplicate dns within this Partition'
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
        verbose_name = 'Partition'
        verbose_name_plural = 'Partitions'

    def __str__(self):
        return self.display_name or super().__str__()

    def get_absolute_url(self):
        return reverse('ipphone:partitions', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.enforce_unique,
            self.description,
        )

    @property
    def display_name(self):
        return self.name
