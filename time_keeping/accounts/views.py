from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView
from django.utils import timezone
from .models import TimeRecord,User
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime


def time_in(request):
    context_dict = {}

    users = User.objects.all()

    context_dict["users"] = users
    if request.session.get('loggedin'):
        return redirect('accounts:time_out')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_authenticated:
                login(request, user)
                time_in = timezone.now()
                request.session['loggedin'] = True
                TimeRecord.objects.create(user=user, time_in=time_in)
                return redirect('accounts:view_records')
            else:
                error_message = "Invalid Credentials or The Account is not Active"
                context_dict['error_message'] = error_message
                return render(request, 'time_in.html', context_dict)
        else:
            if request.session.get('time_in'):
                return redirect('accounts:view_records')
            return render(request, 'time_in.html', context_dict)

@login_required
def time_out(request):
    context_dict = {}

    users = User.objects.all()

    context_dict["users"] = users
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_authenticated:
            if user == request.user:
                logout(request)
                previous_record = user.timerecord_set.latest('time_in')
                time_in = previous_record.time_in
                previous_record.delete()
                time_out = timezone.now()
                duration = time_out - time_in
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                TimeRecord.objects.create(user=user, time_in=time_in, time_out=time_out)
                message = f'Your Time Out is Successfully Recorded. Your time in was {time_in.strftime("%I:%M:%S %p")} and your time out was {time_out.strftime("%I:%M:%S %p")}. Your total time for this day was {hours} hours and {minutes:02d} minutes.'
                messages.success(request, message)
                return redirect('accounts:time_in')
            else:
                error_message = "Invalid logout credentials"
                context_dict['error_message'] = error_message
                return render(request, 'time_out.html', context_dict)
        else:
            error_message = "Invalid logout credentials"
            context_dict['error_message'] = error_message
            return render(request, 'time_out.html', context_dict)
    else:
        time_records = request.user.timerecord_set.all().order_by('-time_in')
        context_dict['time_records'] = time_records
        return render(request, 'time_out.html', context_dict)
    
def time_record_list(request):
    return render(request, 'time_record_list.html')

@login_required
def view_records(request):
    time_records = TimeRecord.objects.filter(user=request.user).order_by('-time_in')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        time_records = time_records.filter(time_in__date__gte=date_from, time_out__date__lte=date_to)

    paginator = Paginator(time_records, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'date_from': date_from,
        'date_to': date_to,
        'user_initials': f"{request.user.first_name[0]}{request.user.last_name[0]}"
    }

    return render(request, 'view_records.html', context)



class TimeRecordListView(ListView):
    model = TimeRecord
    template_name = 'time_record_list.html'


