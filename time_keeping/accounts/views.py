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
from apscheduler.schedulers.background import BackgroundScheduler



def mark_absent_users():
    date = timezone.now().date()
    users = User.objects.all()
    for user in users:
        if not TimeRecord.objects.filter(user=user, time_in__date=date).exists():
            TimeRecord.objects.create(user=user, time_in=None, time_out=None)


scheduler = BackgroundScheduler()
scheduler.add_job(mark_absent_users, 'interval', days=1, start_date='2023-03-24 00:00:00')
scheduler.start()



def time_in(request):
    context_dict = {}
    users = User.objects.all()
    context_dict["users"] = users
    if request.session.get('loggedin'):
        return redirect('accounts:view_records')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_authenticated:
                login(request, user)
                time_in = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                request.session['loggedin'] = True
                TimeRecord.objects.create(user=user, time_in=time_in)
                print(user.position_id)
                if user is not None and user.is_authenticated and user.position_id == 2:
                    return redirect('accounting:account')
                    
                return redirect('accounts:view_records')
            else:
                error_message = "Invalid Credentials or The Account is not Active"
                context_dict['error_message'] = error_message
                return render(request, 'time_in.html', context_dict)
        else:
            if request.session.get('time_in'):
                print(user.position_id)
                return redirect('accounts:view_records')
            return render(request, 'time_in.html', context_dict)

def time_out(request):
    previous_record = request.user.timerecord_set.latest('time_in')
    time_in = previous_record.time_in
    previous_record.delete()
    time_out = timezone.now()
    duration = time_out - time_in
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    TimeRecord.objects.create(user=request.user, time_in=time_in, time_out=time_out)
    message = f'Your Time Out is Successfully Recorded. Your time in was {time_in.strftime("%I:%M:%S %p")} and your time out was {time_out.strftime("%I:%M:%S %p")}. Your total time for this day was {hours} hours and {minutes:02d} minutes.'
    messages.success(request, message)
    logout(request)
    return redirect('accounts:time_in')



def time_record_list(request):
    return render(request, 'time_record_list.html')

@login_required
def view_records(request):
    user = request.user
    if user.position_id == '2':
        return redirect('accounting:account')
    time_records = TimeRecord.objects.filter(user=request.user).order_by('-time_in')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        time_records = time_records.filter(time_in__date__gte=date_from, time_out__date__lte=date_to)

    counts = {
        'late': 0,
        'absent': 0,
        'halfday': 0,
        'undertime': 0,
        'present': 0,
        'overtime': 0,
    }
    print(user.position_id)
    
    for time_record in time_records:
        total_time = time_record.total_time.total_seconds() // 60 if time_record.total_time else None
        if time_out is None:
            counts[''] 
        elif total_time is None:
            counts['absent']+=1 
        elif total_time <= 240:
            counts['halfday'] += 1
        elif total_time >= 300 and total_time < 540:
            counts['undertime'] += 1
        elif total_time >= 540 and total_time < 600:
            counts['present'] += 1
        elif total_time >= 600 and user.position_id  != 4:
            counts['present'] += 1
            overtime = (total_time - 510) // 60 
            counts['overtime'] += overtime if overtime > 0 else 0 
        elif total_time >= 600:
            print(total_time)
            counts['present'] += 1
            overtime = (total_time - 600) // 60 
            counts['overtime'] += overtime if overtime > 0 else 0
            

    paginator = Paginator(time_records, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'date_from': date_from,
        'date_to': date_to,
        'user_initials': f"{request.user.first_name[0]}{request.user.last_name[0]}",
        'counts': counts,
    }


    return render(request, 'view_records.html', context)
    



class TimeRecordListView(ListView):
    model = TimeRecord
    template_name = 'time_record_list.html'
