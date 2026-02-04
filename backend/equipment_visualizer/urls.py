from django.contrib import admin
from django.urls import path, include,re_path
from django.views.generic import TemplateView
from django.http import JsonResponse
urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('equipment_api.urls')),
    path('', lambda request: JsonResponse({"message": "Backend API is running"})),
]


