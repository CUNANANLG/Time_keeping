from django.shortcuts import render,redirect
from accounts.models import User

def Index(request):
    context_dict = {}

    users = User.objects.all()

    context_dict["users"] = users
    if request.session.get('loggedin'):
        return redirect('accounts:time_out')
    return render(request, 'time_in.html',context_dict)


