from django.urls import path
from . import views

app_name = "product"

urlpatterns = [
    path("", views.AfterSalesRecordListView.as_view(), name="aftersales_list"),
    path("create/", views.AfterSalesRecordCreateView.as_view(), name="aftersales_create"),
    path("<int:pk>/", views.AfterSalesRecordDetailView.as_view(), name="aftersales_detail"),
    path("<int:pk>/edit/", views.AfterSalesRecordUpdateView.as_view(), name="aftersales_update"),
    path("<int:pk>/delete/", views.AfterSalesRecordDeleteView.as_view(), name="aftersales_delete"),
    path("export/", views.AfterSalesRecordExportView.as_view(), name="aftersales_export"),
    path("import/", views.AfterSalesRecordImportView.as_view(), name="aftersales_import"),
]