# # urls.py
# from django.urls import path
# from . import views

# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('upload/', views.upload_data, name='upload_data'),
#     path('polling-units/', views.polling_units_list, name='polling_units_list'),
#     path('allocations/', views.allocations_list, name='allocations_list'),
#     path('allocations/create/', views.create_allocation, name='create_allocation'),
#     path('allocations/<int:allocation_id>/', views.view_allocation, name='view_allocation'),
#     path('allocations/<int:allocation_id>/download/', views.download_allocation_excel, name='download_allocation_excel'),
#     path('api/validate-allocation/', views.validate_allocation, name='validate_allocation'),
# ]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_data, name='upload_data'),
    path('polling-units/', views.polling_units_list, name='polling_units_list'),
    path('allocations/', views.allocations_list, name='allocations_list'),
    path('allocations/create/', views.create_allocation, name='create_allocation'),
    path('allocations/<int:allocation_id>/', views.view_allocation_results, name='view_allocation_results'),
    path('allocations/<int:allocation_id>/full-data/', views.view_allocation_full_data, name='view_allocation_full_data'),
    path('allocations/<int:allocation_id>/download/', views.download_allocation_excel, name='download_allocation_excel'),
    path('allocations/<int:allocation_id>/download-pdf/', views.download_allocation_pdf, name='download_allocation_pdf'),
    path('api/validate-allocation/', views.validate_allocation, name='validate_allocation'),
]
