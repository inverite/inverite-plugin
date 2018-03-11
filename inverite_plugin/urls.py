from django.urls import include, path

urlpatterns = [
    path('customer/', include('customer.urls')),
]
