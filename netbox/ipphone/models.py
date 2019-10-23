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

from extras.models import CustomFieldModel, ObjectChange, TaggedItem
from utilities.models import ChangeLoggedModel
from utilities.utils import serialize_object
from .constants import *


class ComponentTemplateModel(models.Model):

    class Meta:
        abstract = True

    def instantiate(self, device):
        """
        Instantiate a new component on the specified Device.
        """
        raise NotImplementedError()

    def to_objectchange(self, action):
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=self.device_type,
            object_data=serialize_object(self)
        )

class ComponentModel(models.Model):
    description = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        abstract = True

    def to_objectchange(self, action):
        # Annotate the parent Device/VM
        try:
            parent = getattr(self, 'device', None) or getattr(self, 'virtual_machine', None)
        except ObjectDoesNotExist:
            # The parent device/VM has already been deleted
            parent = None

        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=parent,
            object_data=serialize_object(self)
        )

    @property
    def parent(self):
        return getattr(self, 'device', None)

class ExtensionManager(models.Manager):

    def search(self):
        return Extension.objects.all()


class Extension(ChangeLoggedModel, CustomFieldModel):
    dn = models.CharField(
        max_length=25,
        help_text='Extension',
        verbose_name='Extension'
    )
    partition = models.ForeignKey(
        to='ipphone.Partition',
        on_delete=models.PROTECT,
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
        'dn', 'partition', 'status', 'description',
    ]

    class Meta:
        ordering = ['id', 'dn', 'partition']
        verbose_name = 'Extension'
        verbose_name_plural = 'Extensions'

    def __str__(self):
        return str(self.dn)

    def get_absolute_url(self):
        return reverse('ipphone:extension', args=[self.pk])

    def get_duplicates(self):
        return Extension.objects.filter(partition=self.partition,dn=self.dn).exclude(pk=self.pk)

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
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            object_data=serialize_object(self)
        )

    def to_csv(self):
        return (
            self.dn,
            self.get_status_display(),
            self.description,
            self.partition,
        )

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


class LineManager(models.Manager):
    def search(self):
        ordering = [
            'name', 'pk'
        ]
        return Line.objects.all().order_by(*ordering)


class Line(ComponentModel):
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='line',
        null=True,
        blank=True
    )
    extension = models.ForeignKey(
        to='ipphone.Extension',
        on_delete=models.SET_NULL,
        related_name='device',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=64
    )
    objects = LineManager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'device', 'name', 'description', 'extension'
    ]

    class Meta:
        ordering = ['device', 'name', 'extension']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipphone:line', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.device.identifier if self.device else None,
            self.name,
            self.description,
            self.extension
        )

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def to_objectchange(self, action):
        # Annotate the parent Device
        try:
            parent_obj = self.extension
        except ObjectDoesNotExist:
            parent_obj = None

        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=parent_obj,
            object_data=serialize_object(self)
        )

    @property 
    def parent(self):
        return self.device

    @property
    def count_extensions(self):
        return self.extension.count()


class LineTemplate(ComponentTemplateModel):
    """
    A template for a physical data line on a new Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.CASCADE,
        related_name='line_templates'
    )
    name = models.CharField(
        max_length=64
    )

    objects = LineManager()

    class Meta:
        ordering = ['device_type', 'name']

    def __str__(self):
        return self.name

    def instantiate(self, device):
        return Interface(
            device=device,
            name=self.name
        )

