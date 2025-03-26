from django.urls import path
from .views import CustomerListView, CustomerDetailView, CancelAppointmentView, BusinessDetailView, ServiceListCreateView, VerifyAppointment, BusinessCreateView

urlpatterns = [

     
    # Business endpoints
    path('verify/', VerifyAppointment.as_view(), name='verify'),
    path('customer/<uuid:business_id>/', CustomerListView.as_view(), name='list-my-customers'),
    path('customer/<uuid:business_id>/c/<int:pk>/', CustomerDetailView.as_view(), name='my-customer'),
    path('cancel/<uuid:business_id>/appointment/', CancelAppointmentView.as_view(), name='cancel'),
    path('my/<uuid:business_id>/business/', BusinessDetailView.as_view(), name='my-business'),
    path('my/<uuid:business_id>/services/', ServiceListCreateView.as_view(), name='my-service'),
    path('create/', BusinessCreateView.as_view(), name='create-business'),
    
]