from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import admin

# Create your views here.
def Index(request):
    return render(request, 'base.html')