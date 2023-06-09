"""time_keeping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import time_in,time_out,TimeRecordListView,view_records

app_name='accounts'

urlpatterns = [
    path('time_in/', time_in, name='time_in'),
    path('time_out/', time_out, name='time_out'),
    path('time_record_list/', TimeRecordListView.as_view(), name='time_record_list'),
    path('view_records/', view_records, name='view_records'),
]

urlpatterns += staticfiles_urlpatterns()