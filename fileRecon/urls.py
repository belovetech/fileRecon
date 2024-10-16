"""
URL configuration for fileRecon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from reconciliation import urls as reconciliation_urls

from django.conf.urls import handler404, handler400
from reconciliation.views import custom_404

# Define the custom handler
handler400 = 'reconciliation.views.custom_404'
handler404 = 'reconciliation.views.custom_404'

urlpatterns = [
    path("api/", include(reconciliation_urls)),
]
