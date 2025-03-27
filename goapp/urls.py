"""
URL configuration for goapp project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi





schema_view = get_schema_view(
   openapi.Info(
      title="Ez 💚 API",
      default_version='v1',
      description="Ez API documentation V1",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@ez.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path("admin/", admin.site.urls),
    path("business/api/", include("core.business.api.urls")),
    path("go/api/", include("core.customer.api.urls")),
    path("", include("core.customer.go.urls")),
] 


if not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# # Custom error views
# handler404 = 'myapp.views.custom_404'
# handler500 = 'myapp.views.custom_500'