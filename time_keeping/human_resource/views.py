from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required


@login_required
def accounting(request):
    user = request.user
    if user.position_id != 2:
        return redirect('accounts:view_records')
    else:
        return render(request, 'human_resource/accounting.html')