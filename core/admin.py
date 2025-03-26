from django.contrib import admin
from .models import Customer, Business, Appointment, Service, ReservedSlot, Employee, Rating, Payment, Subscription, Category, User, BusinessHour

admin.site.register(User)
admin.site.register(Category)



@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('business', 'plan_name', 'billing_cycle', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'plan_name', 'billing_cycle', 'business__name', 'start_date')
    search_fields = ('business__name', 'start_date', 'end_date')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

@admin.register(ReservedSlot)
class ReservedSlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'service', 'employee', 'is_reserved')
    list_filter = ('is_reserved', 'employee__full_name', 'service__title', 'business__name')
    search_fields = ('employee__full_name', 'service__title', 'start_time', 'end_time')
    date_hierarchy = 'start_time'
    ordering = ('-created_at',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'employee', 'slot', 'status', 'is_active')
    list_filter = ('status', 'employee__full_name', 'service__title', 'business__name', 'is_active', 'service__duration')
    search_fields = ('employee__full_name', 'service__title', 'slot__start_time', 'slot__end_time', 'customer__full_name')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'method', 'amount', 'currency', 'status')
    list_filter = ('status', 'method', 'appointment__service__title', 'appointment__service__duration')
    search_fields = ('appointment__customer__full_name', 'appointment__service__title', 'appointment__slot__start_time')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'duration', 'price', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured', 'price', 'duration', 'employee')
    search_fields = ('employee__full_name', 'business__name')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'business', 'role', 'is_active')
    list_filter = ('is_active', 'business', 'role')
    search_fields = ('full_name', 'business__name')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',) 
    
    
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_number', 'address', 'gender', 'user_type', 'is_active')
    list_filter = ('address', 'gender', 'to_business__name')
    search_fields = ('full_name','id_number', 'to_business__name')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',) 
    
       
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'service', 'employee', 'rating')
    list_filter = ('rating_type', 'business', 'employee', 'service', 'user')
    search_fields = ('user', 'business__name', 'service__title', 'employee__full_name')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
class BusinessHourInline(admin.TabularInline):
    model = BusinessHour
    extra = 7
    
class BusinessAdmin(admin.ModelAdmin):
    inlines = [BusinessHourInline]
    list_display = ('name', 'owner', 'category', 'address', 'is_verified', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured', 'category', 'address')
    search_fields = ('owner', 'name', 'category')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)

admin.site.register(Business, BusinessAdmin)
