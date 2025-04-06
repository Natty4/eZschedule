from django.urls import path
from . import views
urlpatterns = [
    path('', views.home_view, name='home'),
    path('businesses/', views.business_list_view, name='business_list'),
    path('businesses/<uuid:business_id>/services/', views.service_list_view, name='service_list'),
    path('businesses/<uuid:business_id>/services/<uuid:service_id>/', views.service_detail_view, name='service_detail'),
    path('booking-form/<uuid:business_id>/<uuid:service_id>/<uuid:staff_id>/<str:date>/<str:time>', views.booking_form_view, name='booking_form'),
    path('businesses/<uuid:business_id>/services/<uuid:service_id>/staff/<uuid:staff_id>/booking/<str:date>/<str:time>/summary/', views.booking_summary_view, name='booking_summary'),
    path('thank_you/<uuid:appointment_id>/', views.thank_you_view, name='thank_you'),
    path('go/chapa/callback/', views.chapa_callback_view, name='chapa_callback'),
]