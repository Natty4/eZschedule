import qrcode
import json
from io import BytesIO
from django.core.files import File
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import timedelta, datetime
from ...models import Business, Service, Employee, ReservedSlot, Customer, Appointment, Payment, Rating, BusinessHour, Category, User
from ...serializers import (
    BusinessSerializer, ServiceSerializer, EmployeeSerializer, 
    ReservedSlotSerializer, CustomerSerializer, AppointmentSerializer, 
    PaymentSerializer, RatingSerializer, BusinessHourSerializer,
    CategorySerializer
    )
from ...utils import generate_available_slots
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes    
from django.http import JsonResponse
from geopy.distance import geodesic

class FindNearbyBusiness(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        try:
            if not request.GET.get('lat') or not request.GET.get('lng'):
                return JsonResponse({'error_message': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            lat = float(request.GET.get('lat'))
            lon = float(request.GET.get('lng'))
            radius_km = float(request.GET.get('radius', 10))  # Default 10km

            user_location = (lat, lon)
            businesses = Business.objects.filter(is_active=True, is_verified=True)            
            businesses_serializer = BusinessSerializer(businesses, many=True)
            nearby_businesses = []
            for business in businesses_serializer.data:
                if business['latitude'] and business['longitude']:
                    business_location = (float(business['latitude']), float(business['longitude']))
                    distance = geodesic(user_location, business_location).km
                    
                    if distance <= radius_km:
                        business['distance'] = round(distance, 2)
                        nearby_businesses.append(business)
            # sort businesses by distance
            nearby_businesses = sorted(nearby_businesses, key=lambda x: x['distance'])
            error_message = None
            success_message = f"{len(nearby_businesses)} businesses found within {radius_km}km radius"
            if not nearby_businesses:
                error_message = f"No businesses found within {radius_km}km radius"
                success_message = None
            return JsonResponse({'businesses': nearby_businesses, 'success_message':success_message, 'error_message': error_message})

        except Exception as e:
            return JsonResponse({'error_message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        categories_serializer = CategorySerializer(categories, many=True)
        
        return Response(categories_serializer.data, status=status.HTTP_200_OK)

class BusinessListAPIView(APIView):
    def get(self, request):
        
         
        businesses = Business.objects.filter(is_active=True, is_verified=True)            
        serializer = BusinessSerializer(businesses, many=True)
        rating = Rating.objects.filter(rating_type="business")
        reviews = RatingSerializer(rating, many=True).data
        for bus in serializer.data:
                bus['reviews'] = [revs for revs in reviews if revs['rating_type'] == 'business' and str(revs["business"]) == bus['id']]
        return Response(serializer.data, status=status.HTTP_200_OK)

class BusinessDetailAPIView(APIView):
    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
            business_serializer = BusinessSerializer(business)
            services = Service.objects.filter(business=business, is_active=True)
            services_serializer = ServiceSerializer(services, many=True)
            employees = Employee.objects.filter(business=business, is_active=True)
            employees_serializer = EmployeeSerializer(employees, many=True)
            business_hours = BusinessHour.objects.filter(business=business)
            business_hours_serializer = BusinessHourSerializer(business_hours, many=True)
            reviews = Rating.objects.filter(business=business_id, rating_type="business")
            reviews_serializer = RatingSerializer(reviews, many=True)
            number_of_services = services.count()
            
            return Response({
                "business": business_serializer.data,
                "number_of_services": number_of_services,
                "services": services_serializer.data,
                "employees": employees_serializer.data,
                "business_hours": business_hours_serializer.data,
                "reviews": reviews_serializer.data
            }, status=status.HTTP_200_OK)
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
        

class ServiceListAPIView(APIView):
    def get(self, request, business_id):
        try:
            business = Business.objects.get(id=business_id)
            services = Service.objects.filter(business=business, is_active=True)
            rating = Rating.objects.filter(business=business_id)
            reviews = RatingSerializer(rating, many=True).data
            serializer = ServiceSerializer(services, many=True)
            
            for ser in serializer.data:
                ser['reviews'] = [revs for revs in reviews if revs['rating_type'] == 'service' and str(revs["service"]) == ser['id']]
                
            return Response(serializer.data)
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
            

class ServiceDetailAPIView(APIView):
    def get(self, request, business_id, service_id):
        try:
            service = Service.objects.get(id=service_id, business_id=business_id)
            professionals = Employee.objects.filter(business_id=business_id, services=service_id, is_active=True)
            rating = Rating.objects.filter(rating_type="employee")
            slot = ReservedSlot.objects.filter(service=service)

            # Get employees assigned to this service
            service_employees = service.employee.all()

            # Get business hours for each worker
            business_hours = {
                str(employee.id): [
                    {
                        'day': business_hour.day.lower(),  # Convert to lowercase for consistency
                        'open_time': business_hour.open_time.strftime("%H:%M"),
                        'close_time': business_hour.close_time.strftime("%H:%M"),
                        'is_closed': business_hour.is_closed
                    }
                    for business_hour in BusinessHour.objects.filter(business=business_id)
                ]
                for employee in professionals
            }

            # Get reserved slots for each worker
            reserved_slots = {
                str(employee.id): [
                    (slot.start_time.strftime("%Y-%m-%d-%H:%M"), slot.end_time.strftime("%Y-%m-%d-%H:%M"))
                    for slot in ReservedSlot.objects.filter(employee=employee, service=service, is_reserved=True)
                ]
                for employee in service_employees
            }

            # Task duration
            task_duration = timedelta(minutes=service.duration)
            
            # Generate available slots considering the current day/time
            available_slots = generate_available_slots(business_hours, reserved_slots, task_duration, [employee.id for employee in service_employees])
            
            # Serialize response data
            service_serializer = ServiceSerializer(service)
            professional_serializer = EmployeeSerializer(professionals, many=True)
            reviews = RatingSerializer(rating, many=True).data
            slot_serializer = ReservedSlotSerializer(slot, many=True)
     
            for pro in professional_serializer.data:
                for avs in available_slots:
                    if str(avs) == pro['id']:
                        pro['available_slots'] = available_slots[avs]
                    else:
                        pass
                pro['reviews'] = [revs for revs in reviews if revs['rating_type'] == 'employee' and str(revs["employee"]) == pro['id']]
                if pro['reviews']:
                    pro['total_rating'] = round(sum( rev['rating'] for rev in pro['reviews'])//len(pro['reviews']), 1)
                
               
            return Response({
                "service": service_serializer.data,
                "professionals": professional_serializer.data,
                
                
            })
        except Service.DoesNotExist:
            return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)
    

class ReserveAppointmentSlot(APIView):
 
    def post(self, request):
    
        data = request.data
        business_id = data.get('business')
        service_id = data.get('service')
        employee_id = data.get('employee')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        customer = data.get('customer')

        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d-%H:%M")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d-%H:%M")
        except ValueError as e:
            return Response(f"Invalid time format: {e}", status=status.HTTP_400_BAD_REQUEST)
        
        try:
            business = get_object_or_404(Business, id=business_id)
            service = get_object_or_404(Service, id=service_id)
            employee = get_object_or_404(Employee, id=employee_id)
        except Exception as e:
            return Response(f"errors: {e}", status=status.HTTP_400_BAD_REQUEST)

        # Get reserved slots for worker
        reserved_slots = {"worker": employee_id, "slots": []}
        all_reserved_slots = ReservedSlot.objects.filter(employee=employee_id, service=service_id, is_reserved=True)
        
        for slot in all_reserved_slots:
            reserved_slots["slots"].append((slot.start_time.strftime("%Y-%m-%d-%H:%M"), slot.end_time.strftime("%Y-%m-%d-%H:%M")))
        
        conflict = any(
            start_time == start and end_time == end and start_time < datetime.now()
            for start, end in reserved_slots['slots']
        )
        
        if not conflict:
            try:
                slot, created = ReservedSlot.objects.get_or_create(
                    business=business,
                    service=service,
                    employee=employee,
                    start_time=start_time,
                    end_time=end_time
                )
                if slot.is_reserved == True:
                    return Response({"error": "Already reserved!, try agin with another time slot.", "error_code": "000", "dev-error": "{'error': 'Slot already created'}", }, status=status.HTTP_400_BAD_REQUEST)
                slot.is_reserved = True
                slot.save()       
                
            except Exception as e:
                print(f"Error: --001 {e}", slot)
                return Response({"error": "Already reserved!, try agin with another time slot. ", "error_code": "001", "dev-error": f"{e}", }, status=status.HTTP_400_BAD_REQUEST)
            try:
                customer_data, created = Customer.objects.get_or_create(
                    full_name=customer.get('full_name'),
                    id_number=customer.get('id_number', None),
                    phone_number=customer.get('phone_number'),
                    # tg_id=customer.get('tg_id'),
                    defaults={
                        'user': customer.get('user', None),
                        'email': customer.get('email', None),
                        'gender': customer.get('gender', 'undefined'),
                        'birth_date': customer.get('birth_date', None),
                        'address': customer.get('address', None),
                        'user_type': customer.get('user_type', 'guest'),
                        'to_business': customer.get('to_business', business),
                    }
                )
            except Exception as e:
                try:
                    slot_data, created = ReservedSlot.objects.get_or_create(
                        business=business,
                        service=service,
                        employee=employee,
                        start_time=start_time,
                        end_time=end_time,
                        is_reserved = True
                    )
                    slot_data.is_reserved = False
                    slot_data.save()
                    print(f"Error: --002 {e}")
                    return Response({"error": f"The data on your id and the one you provided doesn't match! \nPlease correct before proceeding", "error_code": "002", "dev-error": f"{e}", }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    print(f"Error: -- {e}")
                    return Response({"error": "Inappropriate Data","error_code": "003", "dev-error": f"{e}", }, status=status.HTTP_400_BAD_REQUEST)
                    
            
        slot_serializer = ReservedSlotSerializer(slot)
        user_serializer = CustomerSerializer(customer_data)
        
        return Response({
            "slot": slot_serializer.data,
            "user_detail": user_serializer.data
            }, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        try:
            employee = request.GET['employee']
        except:
            employee = None
        
        if not employee:
            reserved_slot = ReservedSlot.objects.all()
        else:
            try:
                reserved_slot = ReservedSlot.objects.filter(employee=employee)
            except:
                return Response({"error": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)   
            
        serializer = ReservedSlotSerializer(reserved_slot, many=True)
        return Response(serializer.data) 



class BookingConfirmationAPIView(APIView):
    def post(self, request):
        data = request.data
        customer_data = data.get("customer")
        appointment_data = data.get("appointment")
        payment_data = data.get("payment") 
        try:
            # Create appointment
            appointment_data["customer"] = customer_data['id']
            appointment_serializer = AppointmentSerializer(data=appointment_data)
            try:
                if appointment_serializer.is_valid():
                    appointment = appointment_serializer.save()
                else:
                    return Response(appointment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:             
                return Response({f"error: fiald to create appointment"}, status=status.HTTP_400_BAD_REQUEST)

            # Create payment
            payment_data["appointment"] = appointment.id
            payment_serializer = PaymentSerializer(data=payment_data)
            try:
                if payment_serializer.is_valid():
                    if payment_serializer.validated_data['method'] == "card":
                        payment_serializer.validated_data['status'] = "completed"  
                    payment = payment_serializer.save()
                    
                    # Update appointment status based on payment status
                    if payment.status == "completed":
                        appointment.status = "confirmed"
                    else:
                        appointment.status = "pending"
                    appointment.save()
                    # appointment_link = str(appointment.id) + '?' + str(customer.id) + '-' + str(payment.id)
                    appointment_link = request.build_absolute_uri(appointment.id)

                    appointment_link = str(appointment.id)
                    return Response({
                        "appointment": appointment_serializer.data,
                        "payment": payment_serializer.data,
                        "invoice_link": appointment_link
                    }, status=status.HTTP_201_CREATED)
                    
                else:
                    return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # customer.delete()
                # appointment.delete()
                return Response({str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class InvoiceAPIView(APIView):
    def get(self, request, appointment_id):
        try:
            # appointment_id = appointment_id
            
            appointment = get_object_or_404(Appointment, id=appointment_id)
            payment = get_object_or_404(Payment, appointment=appointment.id)
            customer_id = appointment.customer.id
            customer = get_object_or_404(Customer, id=customer_id)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            Token = f"{appointment.id}-369-{appointment.service.id}"
            Date = f"{appointment.slot.start_time}"
            Service = f"{appointment.service.title}"
            FullName = f"{appointment.customer.full_name}"
            qr_data = f"Full Name: {FullName}\nService: {Service}\nDate: {Date}\n\nToken: {Token}"
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_code_file = File(buffer, name=f"qr_{str(appointment.id)[0:9]}-ez-{str(appointment.service.id)[9:]}.png")
            # Save QR code to the appointment (optional)
            appointment.qr_code.save(qr_code_file.name, qr_code_file, save=True)

            # Serialize data
            appointment_serializer = AppointmentSerializer(appointment)
            payment_serializer = PaymentSerializer(payment)
            customer_serializer = CustomerSerializer(customer)
            data = customer_serializer.data
            customer_data = {
                "full_name": data["full_name"],
                "phone_number": data["phone_number"],
                "email": data["email"],
                "address": data["address"],
                "gender": data["gender"],
                "user_type": data["user_type"],
                "updated_at": data["updated_at"],
                "Token": Token
                
                
            }
            # Include QR code in the response
            qr_code_url = request.build_absolute_uri(appointment.qr_code.url)

            return Response({
                "customer": customer_data,
                "appointment": appointment_serializer.data,
                "payment": payment_serializer.data,
                "qr_code_url": qr_code_url
            })
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    
class RatingAPIView(APIView):
    def post(self, request, business_id):
        default_user = User.objects.get(id=9)
        data = request.data
        data["employee"] = data.get("staff", None)
        data["service"] = data.get("service", None)
        data['user'] = data.get("user", default_user)

        rating_serializer = RatingSerializer(data=data)
        if rating_serializer.is_valid():
            rating = rating_serializer.save()
            rating.user = data['user']
            rating.save()
            return Response(rating_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    def get(self, request, business_id):
        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)
    
    def put(self, request, business_id):
        
        rating_id = request.data.get("rating_id", None)
        try:
            rating = Rating.objects.get(id=rating_id)
            data = request.data
            if request.user != rating.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            rating_serializer = RatingSerializer(rating, data=data)
            if rating_serializer.is_valid():
                rating = rating_serializer.save()
                return Response(rating_serializer.data)
            else:
                return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Rating.DoesNotExist:
            return Response({"error": "Rating not found"}, status=status.HTTP_404_NOT_FOUND)
        
        











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