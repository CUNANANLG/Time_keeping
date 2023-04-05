from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import TimeRecord,User,MonthlyTotalPresent,Additional_Deductions
from django.core.paginator import Paginator
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from accounts.views import time_out
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse

@login_required
def account(request):

    user = request.user

    if user.position_id != 2:

        return redirect('accounts:view_records')
    
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
            total_present = MonthlyTotalPresent.objects.filter(user=user, month__month=now.month).aggregate(Sum('total_present'))['total_present__sum']
            if total_present is None:
                total_present = 0
            weekly_data = []
            total_absents = 0
            for date in dates:
                time_record = TimeRecord.objects.filter(user=user, date=date).first()
                if time_record:
                    weekly_data.append(time_record.work_status)
                    
                else:
                    weekly_data.append('Absent')
                    total_absents += 1
            data.append({'user': user, 'weekly_data': weekly_data, 'total_present': total_present, 'total_absents': total_absents})
        context = {
                'user': user,
                'dates': dates, 
                'data': data,
                'month_year': month_year,
                'total_present': total_present,
                }
        return render(request, 'attendance.html', context)
    
@login_required
def payslip(request):
    user = request.user
    if user.position_id != 2:
        return redirect('accounts:view_records')
    else:
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        if date_from_str and date_to_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            days_diff = (date_to - date_from).days
        else:
            days_diff = None
        context_dict = {}
        users = User.objects.all()
        context_dict["users"] = users
        if request.method == 'POST':
            username = request.POST.get('username')                    
            user = User.objects.get(username=username)
            now = datetime.now()
            total_present = MonthlyTotalPresent.objects.filter(user=user, month__month=now.month).aggregate(Sum('total_present'))['total_present__sum']
            if total_present is None:
                total_present=0
            salary = user.employee_profile.salary
            basicR=round(400*10,2)
            bimonthly=round(salary/2, 2)
            dailyR=round(salary/20, 2)
            hourlyR=round(salary/20/9, 2)
            otR= round(hourlyR*1.25, 2)
            otHR= round(hourlyR*1.3, 2)
            mis=round(bimonthly-basicR,2)
            #payslip formula
            miss=round(mis/10*total_present,2)
            basicS=round(basicR/10*total_present)
            print(basicS)
            OT=round(0)
            holiday125=round(0)
            UnpaidB=round(0)
            holiday30=round(0)

            #deductions formula
            Absences=round(0)
            allowance=round(0)
            Reimbusement=round(0)
            sss=round(user.edit_employee_profile.sss)
            philhealth=round(user.edit_employee_profile.philhealth)
            pagibig=round( user.edit_employee_profile.pagibig)
            Overpayment=round(0)
            Excess1=round(0)
            Excess2=round(0)
            
            grosspay=round(basicS+miss+OT+holiday125+holiday30+UnpaidB+Reimbusement+allowance)
            TotalDeductions=round(sss+philhealth+pagibig+Overpayment+Excess1+Excess2)
            Netpay=round(grosspay-TotalDeductions+allowance-Absences)
            Netpay_Ub=round(Netpay-UnpaidB)
            Netpay_holiday=round(basicS+miss+allowance-Absences-TotalDeductions)
            Total_NetPay=round(grosspay-Absences-TotalDeductions)

            return JsonResponse({

                'salary': salary,

                'miss': miss, 

                'basicS':basicS,

                'TotalDeductions':TotalDeductions,

                'Netpay':Netpay,

                'Netpay_Ub':Netpay_Ub,

                'Netpay_holiday':Netpay_holiday,

                'grosspay':grosspay,
                
                'Total_NetPay':Total_NetPay,

                'total_present':total_present,

                })
        
        context_dict = {
            "users": users,

            "days_diff": days_diff,
        }
    return render(request, 'payslip.html', context_dict)
@login_required
def employeeprofile(request):
    user = request.user
    if user.position_id != 2:
        return redirect('accounts:view_records')
    context_dict = {}
    users = User.objects.all()
    context_dict["users"] = users
    if request.method == 'POST':

        username = request.POST.get('username')
        user = User.objects.get(username=username)
        request.session['username'] = user.username
        position = user.position.name
        salary = user.employee_profile.salary
        sss =  user.edit_employee_profile.sss
        philhealth =  user.edit_employee_profile.philhealth
        pagibig =  user.edit_employee_profile.pagibig
        late_tardiness = user.edit_employee_profile.late_tardiness
        overtime = user.edit_employee_profile.overtime
        no_of_holiday = user.edit_employee_profile.no_of_holiday
        print(sss)

        bimonthly=round(salary/2, 2)
        dailyR=round(salary/20, 2)
        hourlyR=round(salary/20/9, 2)
        otR= round(hourlyR*1.25, 2)
        otHR= round(hourlyR*1.3, 2)
        basicR=round(400*10,2)
        mis=round(bimonthly-basicR,2)

        return JsonResponse({
            'position': position, 
            'salary': salary,
            'bimonthly': bimonthly, 
            'dailyR': dailyR,
            'hourlyR': hourlyR, 
            'otR': otR,
            'otHR': otHR, 
            'basicR': basicR,
            'mis': mis, 
            'sss': sss,
            'late_tardiness': late_tardiness, 
            'overtime': overtime,
            'no_of_holiday': no_of_holiday, 
            'philhealth': philhealth, 
            'pagibig': pagibig,
        })
    
    return render(request, 'employeeprofile.html', context_dict)



@login_required
def edit_employeeprofile(request):

    user = request.user
    if user.position_id != 2:
        return redirect('accounts:view_records')

    username = request.session.get('username') 
    print(username)
    user = User.objects.get(username=username)

    additional_deductions, created = Additional_Deductions.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.employee_profile.salary = request.POST['new_salary']
        user.employee_profile.save()   
        additional_deductions.late_tardiness = request.POST['late_tardiness']
        additional_deductions.sss = request.POST['sss']
        additional_deductions.overtime = request.POST['overtime']
        additional_deductions.no_of_holiday = request.POST['no_of_holiday']
        additional_deductions.philhealth = request.POST['philhealth']
        additional_deductions.pagibig = request.POST['pagibig']
        additional_deductions.save()
        return redirect('accounting:employeeprofile')

    context_dict = {
        "username": username,
        "salary": user.employee_profile.salary,
        "sss": additional_deductions.sss,
        "late_tardiness": additional_deductions.late_tardiness,
        "overtime": additional_deductions.overtime,
        "no_of_holiday": additional_deductions.no_of_holiday,
        "philhealth": additional_deductions.philhealth, 
        "pagibig": additional_deductions.pagibig,
    }

    return render(request, 'edit_employeeprofile.html', context_dict)





