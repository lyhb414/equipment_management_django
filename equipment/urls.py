from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('check_credentials/', views.CheckCredentialsView.as_view(), name='check_credentials'),

    path('promote_to_admin/', views.PromoteToAdminView.as_view(), name='promote_to_admin'),
    path('demote_from_admin/', views.DemoteFromAdminView.as_view(), name='demote_from_admin'),
    path('check_admin/', views.CheckAdminStatusView.as_view(), name='check_admin'),
    path('promote_to_member/', views.PromoteToMemberView.as_view(), name='promote_to_member'),
    path('demote_from_member/', views.DemoteFromMemberView.as_view(), name='demote_from_member'),
    path('check_member/', views.CheckMemberStatusView.as_view(), name='check_member'),

    path('get_first_name/<str:username>/', views.GetFirstNameView.as_view(), name='get_first_name'),
    path('update_first_name/<str:username>/', views.UpdateFirstNameView.as_view(), name='update_first_name'),
    

    path('equipment/', views.EquipmentListCreate.as_view(), name='equipment_list_create'),
    path('equipment/<int:pk>/', views.EquipmentRetrieveUpdateDestroy.as_view(), name='equipment_retrieve_update_destroy'),
    path('equipment/<int:equipment_id>/borrow/', views.EquipmentBorrow.as_view(), name='equipment_borrow'),
    path('equipment_ids/', views.EquipmentIdListView.as_view(), name='equipment_id_list'),
    path('equipment_search/', views.EquipmentSearchView.as_view(), name='equipment_search'),
    path('equipment_modification_search/', views.EquipmentModificationSearchView.as_view(), name='equipment_modification_search'),
    path('borrow_history/<int:pk>/', views.BorrowHistoryDetailView.as_view(), name='borrow_history_detail'),
    path('borrow_history_search/', views.BorrowHistorySearchView.as_view(), name='borrow_history_search'),
    path('equipment_return/', views.ReturnEquipmentView.as_view(), name='equipment_return'),
    path('equipment_return_all/', views.ReturnAllEquipmentView.as_view(), name='equipment_return_all'),


]
