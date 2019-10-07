from django.urls import path

from extras.views import ObjectChangeLogView
from . import views
from .models import Phone, IPPhonePartition

app_name = 'ipphone'
urlpatterns = [

    # Phones
    path(r'phones/', views.PhoneListView.as_view(), name='phone_list'),
    path(r'phones/add/', views.PhoneCreateView.as_view(), name='phone_add'),
    path(r'phones/bulk-add/', views.PhoneBulkCreateView.as_view(), name='phone_bulk_add'),
    path(r'phones/import/', views.PhoneBulkImportView.as_view(), name='phone_import'),
    path(r'phones/edit/', views.PhoneBulkEditView.as_view(), name='phone_bulk_edit'),
    path(r'phones/delete/', views.PhoneBulkDeleteView.as_view(), name='phone_bulk_delete'),
    path(r'phones/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='phone_changelog', kwargs={'model': Phone}),
    path(r'phones/assign/', views.PhoneAssignView.as_view(), name='phone_assign'),
    path(r'phones/<int:pk>/', views.PhoneView.as_view(), name='phone'),
    path(r'phones/<int:pk>/edit/', views.PhoneEditView.as_view(), name='phone_edit'),
    path(r'phones/<int:pk>/delete/', views.PhoneDeleteView.as_view(), name='phone_delete'),

    # IPPhonePartitions

    path(r'ipphonepartitions/', views.IPPhonePartitionListView.as_view(), name='ipphonepartition_list'),
    path(r'ipphonepartitions/add/', views.IPPhonePartitionCreateView.as_view(), name='ipphonepartition_add'),
    path(r'ipphonepartitions/import/', views.IPPhonePartitionBulkImportView.as_view(), name='ipphonepartition_import'),
    path(r'ipphonepartitions/edit/', views.IPPhonePartitionBulkEditView.as_view(), name='ipphonepartition_bulk_edit'),
    path(r'ipphonepartitions/delete/', views.IPPhonePartitionBulkDeleteView.as_view(), name='ipphonepartition_bulk_delete'),
    path(r'ipphonepartitions/<int:pk>/', views.IPPhonePartitionView.as_view(), name='ipphonepartitions'),
    path(r'ipphonepartitions/<int:pk>/edit/', views.IPPhonePartitionEditView.as_view(), name='ipphonepartition_edit'),
    path(r'ipphonepartitions/<int:pk>/delete/', views.IPPhonePartitionDeleteView.as_view(), name='ipphonepartition_delete'),
    path(r'ipphonepartitions/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='ipphonepartition_changelog', kwargs={'model': IPPhonePartition}),
]
