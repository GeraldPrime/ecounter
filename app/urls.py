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
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', views.signin_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_data, name='upload_data'),
    path('polling-units/', views.polling_units_list, name='polling_units_list'),
    path('create-allocation/', views.create_allocation, name='create_allocation'),
    path('allocations/', views.allocations_list, name='allocations_list'),
    path('allocation-results/<int:allocation_id>/', views.view_allocation_results, name='view_allocation_results'),
    path('allocation-full-data/<int:allocation_id>/', views.view_allocation_full_data, name='view_allocation_full_data'),
    path('download-excel/<int:allocation_id>/', views.download_allocation_excel, name='download_allocation_excel'),
    path('download-pdf/<int:allocation_id>/', views.download_allocation_pdf, name='download_allocation_pdf'),
    path('validate-allocation/', views.validate_allocation, name='validate_allocation'),
]
