from django.urls import path
from .views import (
    BusinessListAPIView, ServiceListAPIView, ServiceDetailAPIView, ReserveAppointmentSlot,
    BookingConfirmationAPIView, InvoiceAPIView, RatingAPIView, BusinessDetailAPIView, CategoryListAPIView,
    FindNearbyBusiness,
    #PaymentAPIView, 
)


urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('businesses/', BusinessListAPIView.as_view(), name='business-list'),
    path('businesses/<uuid:business_id>/', BusinessDetailAPIView.as_view(), name='business-detail'),
    path('businesses/<uuid:business_id>/services/', ServiceListAPIView.as_view(), name='service-list'),
    path('businesses/<uuid:business_id>/services/<uuid:service_id>/', ServiceDetailAPIView.as_view(), name='service-detail'),
    path('reserve/slot/', ReserveAppointmentSlot.as_view(), name='schedule'),
    path('booking/confirm/', BookingConfirmationAPIView.as_view(), name='booking-confirm'),
    path('invoice/<uuid:appointment_id>/', InvoiceAPIView.as_view(), name='invoice'),
    path('rating/<uuid:business_id>/', RatingAPIView.as_view(), name='rating'),
    path('find-nearby-businesses/', FindNearbyBusiness.as_view(), name='find_nearby_businesses'),
    
]