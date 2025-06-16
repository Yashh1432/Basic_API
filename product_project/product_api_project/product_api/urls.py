from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),  # Routes for products
    path('api/', include('categories.urls')),  # Routes for categories
]