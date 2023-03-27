from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import TimeRecord,User,TotalPresent
from django.core.paginator import Paginator
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from accounts.views import time_out
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q





def mark_absent_users():

    today = datetime.today()
    users = User.objects.all()
    for user in users:
        if not TimeRecord.objects.filter(user=user, time_in__date=today).exists():
            TimeRecord.objects.create(user=user, time_in=None, time_out=None)

scheduler = BackgroundScheduler()
scheduler.add_job(mark_absent_users, 'interval', days=1, start_date='2023-03-22 00:00:00')
scheduler.start()

@login_required
def account(request):
    user = request.user
    if user.position_id != 2:
        return redirect('accounts:view_records')
    else:
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
        'absent': 0,
        'halfday': 0,
        'undertime': 0,
        'present': 0,
        'overtime': 0,
        'total_present': 0,
        'total_absent': 0,
    }
    
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
        'counts': counts
    }

    return render(request, 'account.html', context)


@login_required
def attendance(request):
    user = request.user
    if user.position_id != 2:
        return redirect('accounts:view_records')
    else:
        start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())
        end_date = start_date + timedelta(days=6)
        dates = [start_date + timedelta(days=x) for x in range(5)]

        users = User.objects.all()
        data = []
        now = datetime.now()
        month_year = now.strftime("%B %Y")

        for user in users:
            weekly_data = []
            total_present = TotalPresent.objects.filter(user=user, date=timezone.now().date()).first()
            present_count = total_present.present_count if total_present else 0
            for date in dates:
                time_record = TimeRecord.objects.filter(user=user, date=date).first()
                if time_record:
                    weekly_data.append(time_record.work_status)
                else:
                    weekly_data.append('')

            data.append({'user': user, 'weekly_data': weekly_data, 'total_present': total_present, 'present_count': present_count})

        context = {'dates': dates, 'data': data, 'month_year': month_year}

        return render(request, 'attendance.html', context)


