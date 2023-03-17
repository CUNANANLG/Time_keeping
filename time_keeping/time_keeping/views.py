from django.shortcuts import render, redirect
from accounts.models import User

def Index(request):
    context_dict = {}

    users = User.objects.all()

    context_dict["users"] = users
    if request.session.get('loggedin'):
        user = request.user
        if user.position_id == '2':
            return redirect('human_resource:accounting')
        else:
            return redirect('accounts:view_records')
    
    return render(request, 'time_in.html', context_dict)
