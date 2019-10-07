# Generated by Django 2.2.6 on 2019-10-04 17:40

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0075_cable_devices'),
        ('extras', '0025_objectchange_time_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('interface', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='phone', to='dcim.Interface')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Phone Number',
                'verbose_name_plural': 'Phone Numbers',
                'ordering': ['id', 'phone_number'],
            },
        ),
    ]
