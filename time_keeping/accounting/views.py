from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def account(request):
    user = request.user
    if user.position_id != '2':
        return redirect('accounts:view_records')
    else:
        return render(request, 'account.html')
