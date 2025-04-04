from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from whitelist.models import WhitelistApplication
from accounts.models import User
from discord_bot.bot import send_application_result

def staff_required(view_func):
    """Decorator to check if user is staff"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff_member and not request.user.is_superuser:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@staff_required
def dashboard_view(request):
    # Get counts for dashboard stats
    pending_count = WhitelistApplication.objects.filter(status='pending').count()
    approved_count = WhitelistApplication.objects.filter(status='approved').count()
    rejected_count = WhitelistApplication.objects.filter(status='rejected').count()
    total_users = User.objects.count()
    
    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_users': total_users,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
@staff_required
def applications_view(request):
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        applications = WhitelistApplication.objects.all()
    else:
        applications = WhitelistApplication.objects.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/applications.html', context)

@login_required
@staff_required
def application_detail_view(request, application_id):
    application = get_object_or_404(WhitelistApplication, id=application_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')
        
        if action in ['approve', 'reject']:
            application.status = 'approved' if action == 'approve' else 'rejected'
            application.feedback = feedback
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            # If approved, update user's whitelist status
            if action == 'approve':
                user = application.user
                user.is_whitelisted = True
                user.save()
            
            # Send Discord notification
            try:
                send_application_result(application)
                messages.success(request, f"Application has been {application.status}.")
            except Exception as e:
                print(f"Error sending Discord notification: {e}")
                messages.success(request, f"Application has been {application.status}, but there was an error sending the Discord notification.")
            
            return redirect('dashboard_applications')
    
    return render(request, 'dashboard/application_detail.html', {'application': application})

@login_required
@staff_required
def manage_staff_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can manage staff members.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            if action == 'add_staff':
                user.is_staff_member = True
                messages.success(request, f"{user.username} has been added as a staff member.")
            elif action == 'remove_staff':
                user.is_staff_member = False
                messages.success(request, f"{user.username} has been removed from staff.")
            user.save()
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            
    staff_members = User.objects.filter(is_staff_member=True)
    non_staff_users = User.objects.filter(is_staff_member=False)
    
    context = {
        'staff_members': staff_members,
        'non_staff_users': non_staff_users,
    }
    
    return render(request, 'dashboard/manage_staff.html', context)