from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('system-admin/', admin.site.urls),
    path('', include('web.urls'))
]