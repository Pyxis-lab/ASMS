from django.urls import path
from . import views

app_name = 'TrialItem'

urlpatterns = [
    path('', views.TrialItemListView.as_view(), name='trialitem_list'),
    path('detail/<int:pk>/', views.TrialItemDetailView.as_view(), name='trialitem_detail'),
    path('detail/<int:pk>/progress/', views.TrialItemProgressView.as_view(), name='trialitem_progress'),
    path('create/', views.TrialItemCreateView.as_view(), name='trialitem_create'),
    path('update/<int:pk>/', views.TrialItemUpdateView.as_view(), name='trialitem_update'),
    path('delete/<int:pk>/', views.TrialItemDeleteView.as_view(), name='trialitem_delete'),
    path('import/', views.TrialItemImportView.as_view(), name='trialitem_import'),
    path('export/', views.TrialItemExportView.as_view(), name='trialitem_export'),
]