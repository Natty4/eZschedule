import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField 
from django.utils.translation import gettext_lazy as _




class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('business_owner', 'Business Owner'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.first_name + ' ' + self.last_name if self.first_name else self.username


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    to_business = models.ForeignKey('Business', on_delete=models.SET_NULL, null=True, related_name='customers')
    tg_id = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=9, choices=[('M', 'Male'), ('F', 'Female'), ('undefined', 'Unknown')], default='undefined')
    birth_date = models.DateField(null=True, blank=True)
    id_number = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=15, choices=[('guest', 'Guest Customer'), ('authenticated', 'Authenticated Customer')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    
    class Meta:
        unique_together = ('phone_number', 'id_number', 'full_name')
    
    

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)  # Use CloudinaryField instead of ImageField
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    
class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(User, on_delete=models.PROTECT, related_name='businesses', db_index=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='businesses')
    name = models.CharField(max_length=255, db_index=True, unique=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(unique=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)  # Use CloudinaryField
    logo = CloudinaryField('logo', blank=True, null=True)    # Use CloudinaryField for logos
    theme_color = models.CharField(max_length=7, default='#000000')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='employees', db_index=True)
    full_name = models.CharField(max_length=50)
    photo = CloudinaryField('photo', blank=True, null=True)  # Use CloudinaryField
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='services')
    employee = models.ManyToManyField(Employee, related_name='services', blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)  # Use CloudinaryField
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    preliminary_questions_type = models.CharField(max_length=20, choices=[('text', 'Text'), ('choice', 'Choice'), ('boolean', 'Boolean')], default='text')
    preliminary_questions = models.JSONField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BusinessHour(models.Model):
    DAYS = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='hours')
    day = models.CharField(max_length=10, choices=DAYS)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.business.name} - {self.day} - {self.open_time} to {self.close_time}"
    class Meta:
        unique_together = ('business', 'day')
    
    
class ReservedSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reserved_slots')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reserved_slots')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reserved_slots', null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_reserved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.service} - {self.start_time}"
    
    class Meta:
        unique_together = ('business', 'service', 'employee', 'start_time','end_time', 'is_reserved')


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='appointments')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='appointments')
    slot = models.OneToOneField(ReservedSlot, on_delete=models.CASCADE, null=True, blank=True)
    preliminary_answers = models.JSONField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('rescheduled', 'Rescheduled'), ('completed', 'Completed')], default='pending')
    qr_code = CloudinaryField('qr_code', blank=True, null=True)  # Use CloudinaryField for QR codes
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.full_name} - {self.service.title} on {self.slot.start_time}"


class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB', choices=[('ETB', 'ETB'), ('USD', 'USD')])  # Added currency field
    transaction_id = models.CharField(max_length=12, unique=True)
    method = models.CharField(max_length=20, choices=[('card', 'Card'), ('cash', 'Cash'), ('mobile', 'Mobile')], default='card')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.appointment.customer.full_name} - {self.method} - {self.amount} {self.currency}"


class Subscription(models.Model):
    PLAN_CHOICES = [('free', 'Freemium'), ('basic', 'Basic'), ('premium', 'Premium')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('cancelled', 'Cancelled')]

    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='subscription')
    plan_name = models.CharField(max_length=50, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB', choices=[('ETB', 'ETB'), ('USD', 'USD')])  # Added currency field
    billing_cycle = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')  # Added status

    def __str__(self):
        return f"{self.business.name} - {self.plan_name}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} to {self.recipient.email} - {self.status}"


class Rating(models.Model):
    rating_type = models.CharField(max_length=20, choices=[('service', 'Service'), ('business', 'Business'), ('employee', 'Employee')])
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='ratings')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='ratings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='ratings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # unique_together = ('user', 'service', 'employee')
        ordering = ['-created_at']
    
    def clean(self):
        if self.rating_type == 'service' and not self.service:
            raise ValidationError("Service is required for service rating")
        if self.rating_type == 'business' and not self.business:
            raise ValidationError("Business is required for business rating")
        if self.rating_type == 'employee' and not self.employee:
            raise ValidationError("Employee is required for employee rating")
        
    def __str__(self):
        return f"{self.rating_type} - {self.rating} by {self.user}"

