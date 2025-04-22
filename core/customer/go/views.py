import os
import requests
import json
import time
import logging
import string
import random
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.files import File
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse, HttpResponse
from django.http import HttpResponseServerError
from django.urls import reverse
from datetime import timedelta, datetime
from django.conf import settings
import hashlib
from django.views.decorators.csrf import csrf_exempt


# Set up logging
logger = logging.getLogger(__name__)






#API_BASE_URL = settings.API_BASE_URL
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/go/api/')

if settings.DEBUG:
    API_BASE_URL = 'http://localhost:8000/go/api/'





@csrf_exempt
def telegram_login(request):
    # Get data from the request
    data = request.GET.dict()
    if 'hash' not in data:
        return JsonResponse({'error': 'Missing hash'}, status=400)

    # Secret key, should be kept secret and used to verify the hash
    secret = settings.TELEGRAM_BOT_TOKEN  # Bot token or secret can be used here

    # Sort the data by key
    sorted_data = sorted((key, value) for key, value in data.items() if key != 'hash')
    data_str = '\n'.join(f'{key}={value}' for key, value in sorted_data) + '\n'

    # Create the hash
    calculated_hash = hashlib.sha256(data_str.encode('utf-8') + secret.encode('utf-8')).hexdigest()

    # Check if the hashes match
    if calculated_hash != data['hash']:
        return JsonResponse({'error': 'Invalid hash'}, status=400)

    # If hash is valid, proceed with user data
    user_info = {
        'id': data['id'],
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'username': data['username'],
        'photo_url': data['photo_url'],
    }

    user, created = User.objects.get_or_create(telegram_id=data['id'], defaults=user_info)
    if created:
        user.set_password('random_password')  # Set a random password or generate one
        user.save()

    # Return success
    return JsonResponse({'status': 'success', 'user': user_info})


def home_view(request):
    def timed_request(url):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"API request to {url} took {elapsed_time:.2f} seconds") 
        return response
    category_data = {}
    response = timed_request(f'{API_BASE_URL}categories/')
    if response.status_code == 200:
        category_data = response.json()
        
    request.session['categories'] = category_data
    
    return render(request, 'index.html', {'categories': category_data})


# Page 1: Business Listing
def business_list_view(request):
    def timed_request(url):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"API request to {url} took {elapsed_time:.2f} seconds") 
        return response
    category_data = request.session.get('categories')
    category = request.GET.get('category', None)
    search = request.GET.get('search', None)
    response = timed_request(f'{API_BASE_URL}businesses/')
    if response.status_code == 200:
        businesses = response.json()
        businesses_data = {}
        if category:
            businesses_data = [business for business in businesses if category.lower() in business.get('category', '')['name'].lower()]
            success_message = None
            error_message = None
        elif search:
            search = search.lower()
            businesses_data = [
                business for business in businesses
                if any(search in business.get(field, '').lower() for field in ['name', 'description', 'address'])
            ]
            success_message = f"Success! - {len(businesses_data)} - items found"
            error_message = None
        else:
            success_message = None
            error_message = None
            for business in businesses:
                business['num_services'] = len(business.get('services', []))

            return render(request, 'page11.html', {'businesses': businesses, 'success_message':success_message, 'categories': category_data, 'error_message': error_message })
            
        if not businesses_data:
            businesses = businesses
            success_message = None
            error_message = f"Query matching itme not found!"
        else:
            businesses = businesses_data
            
                
        for business in businesses:
            business['num_services'] = len(business.get('services', []))

        return render(request, 'page11.html', {'businesses': businesses, 'categories': category_data, 'success_message':success_message, 'error_message': error_message })
    else:
        raise Http404("Businesses not found")
    
# Page 2: Service Listing
def service_list_view(request, business_id):
    def timed_request(url):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"API request to {url} took {elapsed_time:.2f} seconds") 
        return response

    response = timed_request(f'{API_BASE_URL}businesses/{business_id}/')
    if response.status_code == 200:
        business_data = response.json()
        business = business_data.get('business', {})
        services = business_data.get('services', [])
        staff = business_data.get('employees', [])
        number_of_services = business_data.get('number_of_services', [])
        business_hours = business_data.get('business_hours', [])
        reviews = {}
        reviews['reviews'] = business_data.get('reviews', [])
        if reviews['reviews']:
            reviews['total_rating'] = round(sum( rev['rating'] for rev in reviews['reviews'])/len(reviews['reviews']), 1)
        # Store businesses in the session for use in other views
        request.session['business_data'] = business_data
        return render(request, 'page2.html', {
            'services': services, 
            'business': business, 
            'staff': staff, 
            'number_of_services': number_of_services, 
            'business_hours': business_hours,
            'reviews': reviews
            })
    else:
        raise Http404("Business not found")
    


# Page 3: Service Details and Professional Availability
def service_detail_view(request, business_id, service_id):
        
    def timed_request(url):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"API request to {url} took {elapsed_time:.2f} seconds") 
        return response
    
    error_message = request.GET.get('error', None)
    response = timed_request(f'{API_BASE_URL}businesses/{business_id}/services/{service_id}/')
    
    if response.status_code == 200:
        service_data = response.json()
        service = service_data.get('service', {})
        professionals = service_data.get('professionals', [])
        business = request.session['business_data']['business']
        available_slots_json = json.dumps({prof['id']: prof['available_slots'] for prof in professionals})
        request.session['current_service'] = service
        request.session['current_service']['available_slots_json'] = available_slots_json
        return render(request, 'page3.html', {'service': service, 'professionals': professionals, 'business': business, 'available_slots_json':available_slots_json, 'error_message': error_message})
    else:
        raise Http404("Service not found")
    
    
# Page 4: User Information Form
def booking_form_view(request, business_id, service_id, staff_id, date, time):
    
    start_time, end_time = time.split('-')    
    start_time = date + '-' + start_time.strip()
    end_time = date + '-' + end_time.strip()

    service_data  = request.session.get('current_service')
    staff = {}
    for st in service_data['employee']:
        if st['id'] == str(staff_id):
            staff = st
            pass
   
    if request.method == 'POST':
        customer = {
            "tg_id": request.POST.get("tg_id", None),
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email", None),
            "phone_number": request.POST.get("phone_number"),
            "id_number": request.POST.get("id_number", None),
            "address": request.POST.get("address", None),
            "gender": request.POST.get("gender", None),
            "notes": request.POST.get("notes", None),
            "preliminary_answer": request.POST.get('preliminary_answer', None)
            }
        payload = {
            "employee": str(staff_id),
            "start_time": start_time,
            "end_time": end_time,
            "business":str(business_id),
            "service": str(service_id),
            "customer": customer
            }    
        
        
        response = requests.post(
            f"{API_BASE_URL}reserve/slot/", 
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}  # Set the content type to JSON
            )
    
        if response.status_code == 201:
            notes = customer['notes']
            preliminary_answer = customer['preliminary_answer']
            
        else:
            error = response.json()
            error_message = error.get('error')
            professionals = service_data.get('employee', [])
            available_slots_json = service_data.get('available_slots_json', [])
            business = request.session['business_data']['business']
            if error['error_code'] in ['000', '001']:
                return redirect(f"/businesses/{business_id}/services/{service_id}/?error={error_message}", business_id=business_id, service_id=service_id)
            
            elif error['error_code'] in ['002', '003']:
                return render(request, 'page4.html', {
                'professional': staff_id,
                'service': service_data,
                'date': date,
                'time': time,
                'error_message': error_message, 'user_data': payload })
            else:
                raise HttpResponseServerError("Error in booking")
                # return render(request, 'page4.html', {'professional': staff_id, 'service': service_data, 'date': date, 'time': time, 'error_message': error_message})
                        
          
            
        
        data = response.json()
        service = data['slot']['service']
        staff = data['slot']['employee']
        user_data = data['user_detail']
        data['notes'] = notes
        data['preliminary_answer'] = preliminary_answer
        request.session['user_data'] = data
        
        return redirect('booking_summary', business_id=business_id, service_id=service_id,
                        staff_id=staff_id, date=date, time=time)
    
    elif request.method == 'GET':
        return render(request, 'page4.html', {
            'staff': staff,
            'service': service_data,
            'date': date,
            'time': f"{time}"
        })
        
    else:
        raise Http404("Service or staff not found")

    


def booking_summary_view(request, business_id, service_id, staff_id, date, time):
    user_data = request.session.get('user_data')
    if not user_data:
        return redirect('booking_form', business_id=business_id, service_id=service_id, 
                        staff_id=staff_id, date=date, time=time)

    tx_ref = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))

    service = request.session.get('current_service')
    staff = next((st for st in service['employee'] if st['id'] == str(staff_id)), {})

    booking_fee = 100
    request.session['booking_fee'] = booking_fee

    appointment_data = {
        "appointment": {
            "business": user_data['slot']['business'],
            "service": user_data['slot']['service']['id'],
            "employee": user_data['slot']['employee']['id'],
            "slot": user_data['slot']['id'],
            "notes": user_data['notes'],
            "preliminary_answer": user_data['preliminary_answer']
        },
        "customer": user_data['user_detail'],
        "payment": {
            "amount": booking_fee,
            "currency": "ETB",
            "transaction_id": tx_ref,
            "method": "online",
            "status": "pending"  # Initially set to 'pending'
        }
    }

    # Send the request to the API for booking confirmation
    response = requests.post(
        f'{API_BASE_URL}booking/confirm/',
        data=json.dumps(appointment_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 201:
        appointment_data = response.json()
        appointment_id = appointment_data['appointment']['id']

        return_url = request.build_absolute_uri(f"/thank_you/{appointment_id}/")
        callback_url = request.build_absolute_uri(f"/go/chapa/callback/?tx_ref={tx_ref}&status=success")

        return render(request, 'page55.html', {
            'service': service,
            'staff': staff,
            'user_data': user_data,
            'date': date,
            'time': time,
            'tx_ref': tx_ref,
            'appointment_id': appointment_id,
            'booking_fee': booking_fee,
            'return_url': return_url,
            'callback_url': callback_url,
        })
    else:
        error_message = response.json().get('error', f'Error creating appointment {response.text}')
        return render(request, 'payment_failed.html', {'message': error_message})
    
    
def chapa_callback_view(request):
    tx_ref = request.GET.get('tx_ref')
    status = request.GET.get('status')
    if not status:
        return render(request, 'payment_failed.html', {'message': 'Missing transaction reference or status.'})
    
    api_url = f'{API_BASE_URL}booking/confirm/'  
    data = {
        "tx_ref": tx_ref,
        "status": status,
    }

    response = requests.patch(api_url, json=data, headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        data = response.json()
        appointment = data.get('appointment', {})
        appointment_id = appointment['id']
        if not appointment_id:
            return render(request, 'payment_failed.html', {'message': 'No appointment ID found in response.'})
        return redirect('thank_you', appointment_id=appointment_id)
    elif response.status_code == 400:
        error_message = response.json().get('error', 'Bad request.')
        return render(request, 'payment_failed.html', {'message': error_message})
    else:
        error_message = response.json().get('error', 'Failed to update payment status.')
        return render(request, 'payment_failed.html', {'message': error_message})
    
      
    
def thank_you_view(request, appointment_id):
    # Check if the payment is successful by querying the external API (you might have a way to check this externally)
    response = requests.get(f'{API_BASE_URL}invoice/{appointment_id}/')
    
    if response.status_code == 200:
        # Assuming that the API response contains the relevant data like appointment, payment, etc.
        invoice_data = response.json()

        # Extract details from the invoice data (this data should contain payment and appointment information)
        service = request.session.get('current_service')
        staff_id = invoice_data['appointment']['employee']
        staff = [st for st in service['employee'] if st['id'] == str(staff_id)][0]
        slot = invoice_data['appointment']['slot']
        appointment = invoice_data['appointment']
        customer = invoice_data['customer']
        payment = invoice_data['payment']
        qr_code_url = invoice_data['qr_code_url']
        business = request.session.get('business_data', [])
        date = slot['date']

        # Check if payment is marked as successful
        if payment['status'] != 'completed':
            return render(request, 'payment_failed.html', {'message': 'Payment was not successful.'})
            # return redirect('business_list')

        # Render the page with the successful payment and appointment data
        return render(request, 'page6.html', {
            'appointment': appointment,
            'customer': customer,
            'service': service,
            'staff': staff,
            'date': date,
            'slot': slot,
            'payment': payment,
            'qr': qr_code_url,
            'business_data': business,
            'booking_fee': request.session.get('booking_fee', 100),
            'success_message': "Success!"
        })
    else:
        # If there's an error fetching the invoice data, render an error page
        error_message = response.json().get('error', 'Error fetching invoice')
        return render(request, 'page6.html', {'error_message': error_message})

 

# this view can only be accessed after a successful booking

# def thank_you_view(request, appointment_id):
#     print(request.session, '------------------')
#     if not request.session.get('booking_successful'):
#         return redirect('business_list')
#     response = requests.get(f'{API_BASE_URL}invoice/{appointment_id}/')
#     if response.status_code == 200:
#         invoice_data = response.json()
#         service = request.session.get('current_service')
#         staff_id = invoice_data['appointment']['employee']
#         staff = [st for st in service['employee'] if st['id'] == str(staff_id)][0]
#         slot = invoice_data['appointment']['slot']
#         appointment = invoice_data['appointment']
#         customer = invoice_data['customer']
#         payment = invoice_data['payment']
#         qr_code_url = invoice_data['qr_code_url']
#         business = request.session.get('business_data', [])
#         date = slot['date']
#         time = slot
#         buffer = BytesIO()
#         p = canvas.Canvas(buffer)
#         p.drawString(100, 800, f"Invoice for Appointment #{appointment_id}")
#         p.drawString(100, 780, f"Service: {service['title']}")
#         p.drawString(100, 760, f"Staff: {staff['full_name']}")
#         p.drawString(100, 760, f"Date: {slot}")
#         p.drawString(100, 740, f"Customer: {customer['full_name']}")
#         p.drawString(100, 720, f"Payment Status: {payment['status']}")

#         # # QR Code
#         # qr = qrcode.make(f"Appointment-{appointment_id}")
#         # qr_buffer = BytesIO()
#         # qr.save(qr_buffer, format="PNG")
#         # p.drawImage(qr_code_url, 100, 600, width=100, height=100)

#         # p.showPage()
#         # p.save()
#         # buffer.seek(0)
#         # return HttpResponse(buffer, content_type="application/pdf")
        
#         del request.session['booking_successful']
        
#         return render(request, 'page6.html', {
#             'appointment': appointment,
#             'customer': customer,
#             'service': service,
#             'staff': staff,
#             'date': date,
#             'slot': slot,
#             'payment': payment,
#             'qr': qr_code_url,
#             'business_data': business,
#             'success_message': "Success!"
#         })
#     else:
        
#         data = response.json()
#         return render(request, 'page6.html', {'error_message': data['error']})




