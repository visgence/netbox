from django.urls import path

from extras.views import ObjectChangeLogView
from . import views
from .models import Extension, Partition

app_name = 'ipphone'
urlpatterns = [

    # Extensions
    path(r'extensions/', views.ExtensionListView.as_view(), name='extension_list'),
    path(r'extensions/add/', views.ExtensionCreateView.as_view(), name='extension_add'),
    path(r'extensions/bulk-add/', views.ExtensionBulkCreateView.as_view(), name='extension_bulk_add'),
    path(r'extensions/import/', views.ExtensionBulkImportView.as_view(), name='extension_import'),
    path(r'extensions/edit/', views.ExtensionBulkEditView.as_view(), name='extension_bulk_edit'),
    path(r'extensions/delete/', views.ExtensionBulkDeleteView.as_view(), name='extension_bulk_delete'),
    path(r'extensions/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='extension_changelog', kwargs={'model': Extension}),
    path(r'extensions/assign/', views.ExtensionAssignView.as_view(), name='extension_assign'),
    path(r'extensions/<int:pk>/', views.ExtensionView.as_view(), name='extension'),
    path(r'extensions/<int:pk>/edit/', views.ExtensionEditView.as_view(), name='extension_edit'),
    path(r'extensions/<int:pk>/delete/', views.ExtensionDeleteView.as_view(), name='extension_delete'),

    # Partitions

    path(r'partitions/', views.PartitionListView.as_view(), name='partition_list'),
    path(r'partitions/add/', views.PartitionCreateView.as_view(), name='partition_add'),
    path(r'partitions/import/', views.PartitionBulkImportView.as_view(), name='partition_import'),
    path(r'partitions/edit/', views.PartitionBulkEditView.as_view(), name='partition_bulk_edit'),
    path(r'partitions/delete/', views.PartitionBulkDeleteView.as_view(), name='partition_bulk_delete'),
    path(r'partitions/<int:pk>/', views.PartitionView.as_view(), name='partitions'),
    path(r'partitions/<int:pk>/edit/', views.PartitionEditView.as_view(), name='partition_edit'),
    path(r'partitions/<int:pk>/delete/', views.PartitionDeleteView.as_view(), name='partition_delete'),
    path(r'partitions/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='partition_changelog', kwargs={'model': Partition}),
]
