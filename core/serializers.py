from rest_framework import serializers
from .models import (
    User, Customer, Category, Business, Employee, Service,
    ReservedSlot, Appointment, Payment, Subscription, Notification, Rating, BusinessHour
)
    
    
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']


# Customer Serializer (Linked to User)
class CustomerSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Allows assigning a user

    class Meta:
        model = Customer
        fields = ['id', 'tg_id', 'full_name', 'email', 'gender', 'birth_date', 
                  'id_number', 'phone_number', 'address', 'user_type', 
                  'is_active', 'user', 'to_business', 'updated_at'
                  ]


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url', 'description']  # Include all fields
        read_only_fields = ['id']  # Make id read-only
        
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

# Business Serializer (Linked to Category)
class BusinessSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    category = CategorySerializer(read_only=True)
    services = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), many=True)

    class Meta:
        model = Business
        fields = ['id', 'name', 'description', 'image_url', 'logo_url', 'category', 'address', 
                  'phone_number', 'email', 'website', 'services', 'is_active', 'is_verified', 'theme_color',
                  'latitude', 'longitude', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None


# Employee Serializer (Linked to Business and User)
class EmployeeSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'user', 'business', 'photo_url', 'role', 'is_active']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

# Service Serializer (Linked to Business and Employees)
class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())  
    # employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), many=True)  # Supports multiple employees
    employee = EmployeeSerializer(read_only=True, many=True)  # Supports multiple employees
    

    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'image_url', 'business',
                  'employee', 'duration', 'price', 'preliminary_questions',  
                  'is_active', 'is_featured', 'created_at', 'updated_at'
                  ]
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    
# BusinessHour Serializer (Linked to Business)
class BusinessHourSerializer(serializers.ModelSerializer):
    # business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())  

    class Meta:
        model = BusinessHour
        fields = ["day", "open_time", "close_time", "is_closed"]
        
# ReservedSlot Serializer (Linked to Service and Employee)
class ReservedSlotSerializer(serializers.ModelSerializer):
    # service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all()) 
    # employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())  
     
    service = ServiceSerializer(read_only=True) 
    employee = EmployeeSerializer(read_only=True) 

    class Meta:
        model = ReservedSlot
        fields = '__all__'


# Appointment Serializer (Linked to Customer, Service, Employee, and Slot)
class AppointmentSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())  
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())  
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())  
    slot = serializers.PrimaryKeyRelatedField(queryset=ReservedSlot.objects.all())  
    # slot = ReservedSlotSerializer(read_only=True) 

    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'business', 'service', 'employee', 'slot',
                  'preliminary_answers', 'notes', 'status', 'is_active', 'qr_code_url', 
                  'created_at', 'updated_at'
                  ]

    def get_qr_code_url(self, obj):
        # Directly return the value of qr_code which is a URL string
        return obj.qr_code if obj.qr_code else None
    

# Payment Serializer (Linked to Appointment)
class PaymentSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all())  

    class Meta:
        model = Payment
        fields = '__all__'


# Subscription Serializer (Linked to Business)
class SubscriptionSerializer(serializers.ModelSerializer):
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())  

    class Meta:
        model = Subscription
        fields = '__all__'


# Notification Serializer (Linked to Recipient and Appointment)
class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  
    appointment = serializers.PrimaryKeyRelatedField(queryset=Appointment.objects.all())  

    class Meta:
        model = Notification
        fields = '__all__'


# Rating Serializer (Linked to User, Business, Employee, and Service)
class RatingSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  
    user = UserSerializer(read_only=True) 
    business = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())  
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)  # Employee is optional
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), allow_null=True)  # Service is optional

    class Meta:
        model = Rating
        fields = ['id', 'user', 'business', 'employee', 'service', 'rating_type', 'rating', 'comment', 'updated_at']
        
    