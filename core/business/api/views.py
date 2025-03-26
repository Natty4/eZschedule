import qrcode
from io import BytesIO
from django.core.files import File
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import timedelta, datetime
from ...models import Business, Service, Employee, ReservedSlot, Customer, Appointment, Payment, Rating, BusinessHour, Subscription
from ...serializers import BusinessSerializer, ServiceSerializer, EmployeeSerializer, ReservedSlotSerializer, CustomerSerializer, AppointmentSerializer, PaymentSerializer, RatingSerializer, BusinessHourSerializer, SubscriptionSerializer
from ...utils import generate_available_slots
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes     





"""
Business Facing Views 

"""
# -------- BUSINESS MANAGEMENT -------- #


class BusinessCreateView(APIView):
    def post(self, request):
        data = request.data
        business_serializer = BusinessSerializer(data=data['business'])
        subscription_plan = data['subscription_plan']

        try:
            if business_serializer.is_valid():
                business = business_serializer.save()
                business_id = business.id
                start_date = datetime.now()
                
                if subscription_plan == 'basic':
                    
                    subscription_data = {
                        "business": business_id,
                        "plan_name": "basic",
                        "price": 300,
                        "currency": "ETB",
                        "billing_cycle": "monthly",
                        "end_date": start_date + timedelta(days=90),
                        "status": "active"
                    }
                    
                elif subscription_plan == 'premium':
                    subscription_data = {
                        "business": business_id,
                        "plan_name": "premium",
                        "price": 1000,
                        "currency": "ETB",
                        "billing_cycle": "yearly",
                        "end_date": start_date + timedelta(days=365),
                        "status": "active"
                    }
                
                elif subscription_plan == 'free':
                    subscription_data = {
                        "business": business_id,
                        "plan_name": "free",
                        "price": 0,
                        "currency": "ETB",
                        "billing_cycle": "monthly",
                        "end_date": start_date + timedelta(days=30),
                        "status": "active"
                    } 
                    
                else:
                    business_serializer.delete()
                    return Response({"error": "missing subscription plan"}, status=status.HTTP_400_BAD_REQUEST)
                
                subscription_serializer = SubscriptionSerializer(data=subscription_data)
                
                if subscription_serializer.is_valid():
                    business.is_active = True
                    business.save()
                    subscription_serializer.save()
                    return Response({
                        "business": business_serializer.data, 
                        "subscription": subscription_serializer.data
                        }, status=status.HTTP_201_CREATED)
                else:
                    business_serializer.delete()
                    return Response(subscription_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response(business_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
                
            
        except Exception as e:
            return Response({
                    "error": f"{e}",    
                
            }, status=status.HTTP_400_BAD_REQUEST)
            
                

@permission_classes([permissions.IsAuthenticated])
class BusinessDetailView(APIView):
    def get(self, request, business_id):
        owner = request.user
        try:
            if owner.role in ['business_owner', 'admin'] and business_id == owner.businesses.id:
                business = get_object_or_404(Business, pk=business_id, owner=owner)
                service = Service.objects.filter(business__owner=owner)
                employee = Employee.objects.filter(business__owner=owner)
                appointment = Appointment.objects.filter(business__owner=owner)
                reserved_slot = ReservedSlot.objects.filter(business__owner=owner)
                customer = Customer.objects.filter(to_business__owner=owner)
                review = Rating.objects.filter(business__owner=owner, rating_type="business")
                
                service_serializer = ServiceSerializer(service, many=True)
                employee_serializer = EmployeeSerializer(employee, many=True)
                appointment_serializer = AppointmentSerializer(appointment, many=True)
                reserved_slot_serializer = ReservedSlotSerializer(reserved_slot, many=True)
                customer_serializer = CustomerSerializer(customer, many=True)
                review_serializer = RatingSerializer(review, many=True)
                
                return Response({
                        "services": service_serializer.data,
                        "appointment": appointment_serializer.data,
                        "reserved_slots": reserved_slot_serializer.data,
                        "employees": employee_serializer.data,
                        "customer": customer_serializer.data,
                        "reviews": review_serializer.data
                    })
                
            else:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)


        
@permission_classes([permissions.IsAuthenticated])
class ServiceListCreateView(APIView):
    serializer = ServiceSerializer()
    def post(self, request, business_id):
        data = request.data
        service_serialize = ServiceSerializer(data=data)
        if service_serialize.is_valide():
            service_serialize.save()
            return Response(service_serializer.data, status=HTTP_201_CREATED)
        else:
            return Response(service_serialize.error, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, business_id):
        service_id = request.data.get("service_id", None)
        try:
            service_data = Service.objects.get(id=service_id)
            data = request.data
            service_data.id = data.get('service_id', service_data.id)
            service_data.business = data.get('business', service_data.business)
            # service_data.employee = data.get('employee', service_data.employee.all())
            service_data.title = data.get('title', service_data.title)
            service_data.description = data.get('description', service_data.description)
            service_data.image = data.get('image', service_data.image)
            service_data.price = data.get('price', service_data.price)
            service_data.duration = data.get('duration', service_data.duration)
            service_data.preliminary_questions_type = data.get('preliminary_questions_type', service_data.preliminary_questions_type)
            service_data.preliminary_questions = data.get('preliminary_questions', service_data.preliminary_questions)
            print(service_data.title, service_data.business, '=------', service_data.employee.all())
            
            if request.user != service_data.business.owner:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            service_serializer = ServiceSerializer(service_data, data=service_data)
            if service_serializer.is_valid():
                service = service_serializer.save()
                return Response(service_serializer.data)
            else:
                return Response(service_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request, business_id):
        service = Service.objects.filter(business=business_id)
        service_serializer = ServiceSerializer(service, many=True)
        if not request.user.is_authenticated or  request.user.role not in ['business_owner', 'admin']:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response({"services": service_serializer.data}, status=status.HTTP_200_OK)
        
        


# -------- CUSTOMER MANAGEMENT -------- #


@permission_classes([permissions.IsAuthenticated])
class CustomerListView(APIView):
    def get(self, request, business_id):
        user = request.user
        business = get_object_or_404(Business, pk=business_id, owner=user)
        if user.role in ['business_owner', 'admin'] and business.id == business_id:
            customers = Customer.objects.filter(to_business__owner=user)
            serializer = CustomerSerializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
    
    
    
@permission_classes([permissions.IsAuthenticated])
class CustomerDetailView(APIView):
    def get(self, request, business_id, pk):
        user = request.user
        customer = get_object_or_404(Customer, pk=pk, to_business__owner=user)

        # Ensure only authorized users can view customer details
        if user.role not in ['business_owner', 'admin'] :
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CustomerSerializer(customer)
        customer_detail = serializer.data
        appointments = Appointment.objects.filter(business=business_id, customer=customer)
        pending_app = []
        confirmed_app = []
        completed_app = []
        rescheduled_app = []
        cancelled_app = []
        
        appointments_serializer = AppointmentSerializer(appointments, many=True)
        for app in appointments_serializer.data:
            if app['status'] == 'pending':
                pending_app.append(app)
            elif app['status'] == 'confirmed':
                confirmed_app.append(app)
            elif app['status'] == 'completed':
                completed_app.append(app)
            elif app['status'] == 'rescheduled':
                rescheduled_app.append(app)   
            else:
                cancelled_app.append(app) 
        customer_data = {
            "full_name": customer_detail['full_name'],
            "phone_number": customer_detail['phone_number'],
            "address": customer_detail['address'],
            "email": customer_detail['email'],
            "gender": customer_detail['gender'],
            "address": customer_detail['address']
            
        }
        
        analysis_data = {
            "pending_app": len(pending_app),
            "confirmed_app": len(confirmed_app),
            "completed_app": len(completed_app),
            "rescheduled_app": len(rescheduled_app),
            "cancelled_app": len(cancelled_app)
        }
            
        return Response({
            "customer": customer_data,
            "numbers": analysis_data,
            "appointments": appointments_serializer.data
        }, status=status.HTTP_200_OK)
        
        
        
        
        

# -------- APPOINTMENT CANCELLATION -------- #

# @api_view(['PATCH'])
# @permission_classes([permissions.IsAuthenticated])
# def cancel_appointment(request, business_id):
#     """Cancel an appointment (apply cancellation fee if necessary)."""
#     user = request.user
#     data = request.data
    
#     try:
#         app_id = data.get('appointment')
#         business = data.get('business')
#         if str(business) == str(business_id):
#             appointment = get_object_or_404(Appointment, id=app_id)
#             # Only the customer or business owner can cancel
#             if (user != appointment.business.owner and user.role not in ['business_owner', 'admin']) or user != appointment.customer.user:
#                 return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
#             if appointment.status != 'pending' or not appointment.is_active :
#                 return Response({'error': 'Can\'t cancell this appointment'}, status=status.HTTP_403_FORBIDDEN)

#             appointment.status = 'cancelled'
#             appointment.is_active = False
#             appointment.save()
#             return Response({'message': 'Appointment cancelled successfully.'}, status=status.HTTP_200_OK)
#         else:
#            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
#     except Exception as e:
#         return Response(f"error: {e}")
    
    
@permission_classes([permissions.IsAuthenticated])
class CancelAppointmentView(APIView):
    def patch(self, request, business_id):
        user = request.user
        data = request.data
        
        try:
            app_id = data.get('appointment')
            business = data.get('business')
            if str(business) == str(business_id):
                appointment = get_object_or_404(Appointment, id=app_id)
                # Only the customer or business owner can cancel
                if (user != appointment.business.owner and user.role not in ['business_owner', 'admin']) or user != appointment.customer.user:
                    return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
                if appointment.status != 'pending' or not appointment.is_active :
                    return Response({'error': 'Can\'t cancell this appointment'}, status=status.HTTP_403_FORBIDDEN)

                appointment.status = 'cancelled'
                appointment.is_active = False
                appointment.save()
                return Response({'message': 'Appointment cancelled successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(f"error: {e}")

    



@permission_classes([permissions.IsAuthenticated])
class VerifyAppointment(APIView):
 
    def get(self, request):
        try:
            data = request.GET['token']
            appointment_id, service_id = data.split('-369-')
            appointment = Appointment.objects.get(id = appointment_id, status='confirmed', is_active=True)
            payment = Payment.objects.get(appointment = appointment_id, status='pending')
            if request.user.role not in ['business_owner', 'admin'] or request.user != appointment.business.owner:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            task_duartion = timedelta(minutes=appointment.service.duration)
            compensation_minutes = timedelta(minutes=15)
            current_time = datetime.now()
            time_data = (task_duartion + appointment.slot.start_time) - compensation_minutes
            time_data = datetime.strptime(time_data.strftime("%Y-%m-%d-%H:%M"), "%Y-%m-%d-%H:%M")
            current_time = datetime.strptime(current_time.strftime("%Y-%m-%d-%H:%M"), "%Y-%m-%d-%H:%M")
            if time_data <= current_time:
                appointment.status = "cancelled"
                appointment.is_active = False
                appointment.save()
                # payment.status = "failed"
                # payment.save()
                return Response({f"error: appointment not found, already been cancelled !, try next available time slot"}, status=status.HTTP_404_NOT_FOUND)
            if str(service_id) == str(appointment.service.id):
                data = appointment
                appointment_data = {
                    "Full Name: ": appointment.customer.full_name,
                    "Service: ": appointment.service.title,
                    "Employee: ": appointment.employee.full_name,
                    "appointment: ": {"start": appointment.slot.start_time, "end": appointment.slot.end_time}
                    
                }
                
                appointment.status = "completed"
                appointment.is_active = False
                appointment.save()
                payment.status = "completed"
                payment.save()
            else:
                return Response(f"Invalid QR Data please try agin with the correct QR code for {appointment.service}")
            
        except Exception as e:
            return Response({"error": f"bad request, missing {e} "}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(f"{appointment_data}", status=status.HTTP_200_OK)








# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from django.utils.timezone import now
# from django.db import transaction
# from django.http import HttpResponse
# from io import BytesIO
# from reportlab.pdfgen import canvas
# import qrcode
# from datetime import timedelta
# from icalendar import Calendar, Event
# import json

# from .models import Customer, Business, Appointment, Service, ReservedSlot
# from .serializers import CustomerSerializer, AppointmentSerializer, BusinessSerializer


# # -------- BUSINESS VIEWS -------- #

# @api_view(['GET'])
# def business_list(request):
#     """Retrieve list of businesses with optional filtering."""
#     businesses = Business.objects.all()

#     featured = request.GET.get('featured')
#     category = request.GET.get('category')

#     if featured:
#         businesses = businesses.filter(is_featured=True)

#     if category:
#         businesses = businesses.filter(category__name=category)

#     serializer = BusinessSerializer(businesses, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def business_detail(request, business_id):
#     """Retrieve details of a specific business."""
#     business = get_object_or_404(Business, id=business_id)
#     serializer = BusinessSerializer(business)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# # -------- SERVICE VIEWS -------- #

# @api_view(['GET'])
# def service_list(request, business_id):
#     """List services offered by a business."""
#     business = get_object_or_404(Business, id=business_id)
#     services = business.services.all()

#     data = [{"id": s.id, "name": s.name, "description": s.description} for s in services]
#     return Response(data, status=status.HTTP_200_OK)


# # -------- AVAILABILITY CHECK -------- #

# @api_view(['GET'])
# def check_availability(request):
#     """Check available appointment slots for a service (and optional employee)."""
#     service_id = request.GET.get("service_id")
#     employee_id = request.GET.get("employee_id", None)

#     slots = AppointmentSlot.objects.filter(service_id=service_id, start_time__gte=now())

#     if employee_id:
#         slots = slots.filter(employee_id=employee_id)

#     data = [{"slot_id": slot.id, "start_time": slot.start_time, "end_time": slot.end_time} for slot in slots]
#     return Response({"available_slots": data}, status=status.HTTP_200_OK)


# # -------- CUSTOMER DETAILS -------- #

# @api_view(['POST'])
# def submit_details(request):
#     """Store user details for appointment booking."""
#     data = request.data
#     user = request.user if request.user.is_authenticated else None

#     personal_details = {
#         "full_name": user.get_full_name() if user else data.get("full_name"),
#         "email": user.email if user else data.get("email"),
#         "phone": user.profile.phone if user else data.get("phone"),
#         "address": user.profile.address if user else data.get("address"),
#         "custom_answers": data.get("custom_answers", {})
#     }

#     return Response({"message": "Details saved", "details": personal_details}, status=status.HTTP_200_OK)


# # -------- APPOINTMENT BOOKING -------- #

# def process_payment(amount, payment_method):
#     """Dummy payment function (Replace with actual integration)."""
#     return {"status": "success", "transaction_id": "TXN12345"}


# @api_view(['POST'])
# def confirm_appointment(request):
#     """Confirm an appointment with payment."""
#     data = request.data
#     user = request.user if request.user.is_authenticated else None

#     # Process Payment
#     payment_result = process_payment(data["amount"], data["payment_method"])
#     if payment_result["status"] != "success":
#         return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

#     # Store appointment
#     with transaction.atomic():
#         appointment = Appointment.objects.create(
#             user=user,
#             service_id=data["service_id"],
#             employee_id=data.get("employee_id"),
#             scheduled_time=data["scheduled_time"],
#             details=data["details"],
#             status="confirmed",
#             payment_status="paid",
#             transaction_id=payment_result["transaction_id"]
#         )

#     return Response({"message": "Appointment confirmed", "appointment_id": appointment.id}, status=status.HTTP_201_CREATED)


# # -------- INVOICE GENERATION -------- #

# def generate_invoice(request, appointment_id):
#     """Generate a PDF invoice for an appointment."""
#     appointment = get_object_or_404(Appointment, id=appointment_id)

    # buffer = BytesIO()
    # p = canvas.Canvas(buffer)
    # p.drawString(100, 800, f"Invoice for Appointment #{appointment.id}")
    # p.drawString(100, 780, f"Service: {appointment.service.name}")
    # p.drawString(100, 760, f"Date: {appointment.scheduled_time}")
    # p.drawString(100, 740, f"Customer: {appointment.details['full_name']}")
    # p.drawString(100, 720, f"Payment Status: {appointment.payment_status}")

    # # QR Code
    # qr = qrcode.make(f"Appointment-{appointment.id}")
    # qr_buffer = BytesIO()
    # qr.save(qr_buffer, format="PNG")
    # p.drawImage(qr_buffer, 100, 600, width=100, height=100)

    # p.showPage()
    # p.save()
    # buffer.seek(0)
    # return HttpResponse(buffer, content_type="application/pdf")


# # -------- EXPORT CALENDAR FILE -------- #

# def export_calendar(request, appointment_id):
#     """Export an appointment as an .ics calendar event."""
#     appointment = get_object_or_404(Appointment, id=appointment_id)

#     cal = Calendar()
#     event = Event()
#     event.add('summary', f"Appointment with {appointment.service.name}")
#     event.add('dtstart', appointment.scheduled_time)
#     event.add('dtend', appointment.scheduled_time + timedelta(minutes=30))
#     event.add('description', f"Appointment for {appointment.service.name}")
#     cal.add_component(event)

#     response = HttpResponse(cal.to_ical(), content_type='text/calendar')
#     response['Content-Disposition'] = 'attachment; filename="appointment.ics"'
#     return response


# # -------- CUSTOMER MANAGEMENT -------- #

# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def customer_list(request):
#     """List customers (Only for business owners or admins)."""
#     if request.user.role not in ['business_owner', 'admin']:
#         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

#     customers = Customer.objects.filter(to_business__owner=request.user)
#     serializer = CustomerSerializer(customers, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def customer_detail(request, pk):
#     """Retrieve a specific customer."""
#     customer = get_object_or_404(Customer, pk=pk)

#     # Ensure only authorized users can view customer details
#     if request.user.role not in ['business_owner', 'admin']:
#         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

#     serializer = CustomerSerializer(customer)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# # -------- APPOINTMENT CANCELLATION -------- #

# @api_view(['PATCH'])
# @permission_classes([permissions.IsAuthenticated])
# def cancel_appointment(request, pk):
#     """Cancel an appointment (apply cancellation fee if necessary)."""
#     appointment = get_object_or_404(Appointment, pk=pk)

#     # Only the customer or business owner can cancel
#     if request.user != appointment.customer.user and request.user.role not in ['business_owner', 'admin']:
#         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

#     appointment.status = 'cancelled'
#     appointment.save()
#     return Response({'message': 'Appointment cancelled successfully.'}, status=status.HTTP_200_OK)







# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from django.utils.timezone import now
# from django.db import transaction
# from django.http import HttpResponse
# from io import BytesIO
# from reportlab.pdfgen import canvas
# import qrcode
# from datetime import timedelta
# from icalendar import Calendar, Event
# import json

# from .models import Customer, Business, Appointment, Service, AppointmentSlot
# from .serializers import CustomerSerializer, AppointmentSerializer, BusinessSerializer


# # -------- BUSINESS VIEWS -------- #

# @api_view(['GET'])
# def business_list(request):
#     """Retrieve list of businesses with optional filtering."""
#     businesses = Business.objects.all()

#     featured = request.GET.get('featured')
#     category = request.GET.get('category')

#     if featured:
#         businesses = businesses.filter(is_featured=True)

#     if category:
#         businesses = businesses.filter(category__name=category)

#     serializer = BusinessSerializer(businesses, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def business_detail(request, business_id):
#     """Retrieve details of a specific business."""
#     business = get_object_or_404(Business, id=business_id)
#     serializer = BusinessSerializer(business)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# # -------- SERVICE VIEWS -------- #

# @api_view(['GET'])
# def service_list(request, business_id):
#     """List services offered by a business."""
#     business = get_object_or_404(Business, id=business_id)
#     services = business.services.all()

#     data = [{"id": s.id, "name": s.name, "description": s.description} for s in services]
#     return Response(data, status=status.HTTP_200_OK)


# # -------- AVAILABILITY CHECK -------- #

# @api_view(['GET'])
# def check_availability(request):
#     """Check available appointment slots for a service (and optional employee)."""
#     service_id = request.GET.get("service_id")
#     employee_id = request.GET.get("employee_id", None)

#     slots = AppointmentSlot.objects.filter(service_id=service_id, start_time__gte=now())

#     if employee_id:
#         slots = slots.filter(employee_id=employee_id)

#     data = [{"slot_id": slot.id, "start_time": slot.start_time, "end_time": slot.end_time} for slot in slots]
#     return Response({"available_slots": data}, status=status.HTTP_200_OK)


# # -------- CUSTOMER DETAILS -------- #

# @api_view(['POST'])
# def submit_details(request):
#     """Store user details for appointment booking."""
#     data = request.data
#     user = request.user if request.user.is_authenticated else None

#     personal_details = {
#         "full_name": user.get_full_name() if user else data.get("full_name"),
#         "email": user.email if user else data.get("email"),
#         "phone": user.profile.phone if user else data.get("phone"),
#         "address": user.profile.address if user else data.get("address"),
#         "custom_answers": data.get("custom_answers", {})
#     }

#     return Response({"message": "Details saved", "details": personal_details}, status=status.HTTP_200_OK)


# # -------- APPOINTMENT BOOKING -------- #

# def process_payment(amount, payment_method):
#     """Dummy payment function (Replace with actual integration)."""
#     return {"status": "success", "transaction_id": "TXN12345"}


# @api_view(['POST'])
# def confirm_appointment(request):
#     """Confirm an appointment with payment."""
#     data = request.data
#     user = request.user if request.user.is_authenticated else None

#     # Process Payment
#     payment_result = process_payment(data["amount"], data["payment_method"])
#     if payment_result["status"] != "success":
#         return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

#     # Store appointment
#     with transaction.atomic():
#         appointment = Appointment.objects.create(
#             user=user,
#             service_id=data["service_id"],
#             employee_id=data.get("employee_id"),
#             scheduled_time=data["scheduled_time"],
#             details=data["details"],
#             status="confirmed",
#             payment_status="paid",
#             transaction_id=payment_result["transaction_id"]
#         )

#     return Response({"message": "Appointment confirmed", "appointment_id": appointment.id}, status=status.HTTP_201_CREATED)


# # -------- INVOICE GENERATION -------- #

# def generate_invoice(request, appointment_id):
#     """Generate a PDF invoice for an appointment."""
#     appointment = get_object_or_404(Appointment, id=appointment_id)

#     buffer = BytesIO()
#     p = canvas.Canvas(buffer)
#     p.drawString(100, 800, f"Invoice for Appointment #{appointment.id}")
#     p.drawString(100, 780, f"Service: {appointment.service.name}")
#     p.drawString(100, 760, f"Date: {appointment.scheduled_time}")
#     p.drawString(100, 740, f"Customer: {appointment.details['full_name']}")
#     p.drawString(100, 720, f"Payment Status: {appointment.payment_status}")

#     # QR Code
#     qr = qrcode.make(f"Appointment-{appointment.id}")
#     qr_buffer = BytesIO()
#     qr.save(qr_buffer, format="PNG")
#     p.drawImage(qr_buffer, 100, 600, width=100, height=100)

#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return HttpResponse(buffer, content_type="application/pdf")


# # -------- EXPORT CALENDAR FILE -------- #

# def export_calendar(request, appointment_id):
#     """Export an appointment as an .ics calendar event."""
#     appointment = get_object_or_404(Appointment, id=appointment_id)

#     cal = Calendar()
#     event = Event()
#     event.add('summary', f"Appointment with {appointment.service.name}")
#     event.add('dtstart', appointment.scheduled_time)
#     event.add('dtend', appointment.scheduled_time + timedelta(minutes=30))
#     event.add('description', f"Appointment for {appointment.service.name}")
#     cal.add_component(event)

#     response = HttpResponse(cal.to_ical(), content_type='text/calendar')
#     response['Content-Disposition'] = 'attachment; filename="appointment.ics"'
#     return response


# # -------- CUSTOMER MANAGEMENT -------- #

# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def customer_list(request):
#     """List customers (Only for business owners or admins)."""
#     if request.user.role not in ['business_owner', 'admin']:
#         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

#     customers = Customer.objects.filter(to_business__owner=request.user)
#     serializer = CustomerSerializer(customers, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def customer_detail(request, pk):
#     """Retrieve a specific customer."""
#     customer = get_object_or_404(Customer, pk=pk)

#     # Ensure only authorized users can view customer details
#     if request.user.role not in ['business_owner', 'admin']:
#         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

#     serializer = CustomerSerializer(customer)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# # -------- APPOINTMENT CANCELLATION -------- #

# @api_view(['PATCH'])
# @permission_classes([permissions.IsAuthenticated])
# def cancel_appointment(request, pk):
#     """Cancel an appointment (apply cancellation fee if necessary)."""
#     appointment = get_object_or_404(Appointment, pk=pk)

#     # Only the customer or business owner can cancel
#     if request.user != appointment.customer.user and request.user.role not in ['business_owner', 'admin']:
#         return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

#     appointment.status = 'cancelled'
#     appointment.save()
#     return Response({'message': 'Appointment cancelled successfully.'}, status=status.HTTP_200_OK)