from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from whitelist.models import WhitelistApplication
from accounts.models import User
from discord_bot.bot import send_application_result
from django.core.paginator import Paginator
from .models import LogEntry
from jobs.models import JobApplication
from jobs.views import can_access_review_list

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
    # Whitelist application counts
    pending_whitelist_count = WhitelistApplication.objects.filter(status='pending').count()
    approved_whitelist_count = WhitelistApplication.objects.filter(status='approved').count()
    rejected_whitelist_count = WhitelistApplication.objects.filter(status='rejected').count()
    total_users = User.objects.count()
    
    # Get job apps queryset user can review
    job_apps_queryset = JobApplication.objects.select_related('applicant').order_by('-submitted_at')
    allowed_job_types = [] # Keep track for filtering
    if not request.user.is_superuser:
        can_review_sasp = request.user.groups.filter(name="SASP Reviewers").exists()
        can_review_ems = request.user.groups.filter(name="EMS Reviewers").exists()
        can_review_mech = request.user.groups.filter(name="Mechanic Reviewers").exists()
        if can_review_sasp: allowed_job_types.append('SASP')
        if can_review_ems: allowed_job_types.append('EMS')
        if can_review_mech: allowed_job_types.append('MECHANIC')
        job_apps_queryset = job_apps_queryset.filter(job_type__in=allowed_job_types)
    
    pending_job_apps_count = job_apps_queryset.filter(status='PENDING').count()
    user_can_review_jobs = can_access_review_list(request.user)

    # Get recent job applications (that user can review)
    recent_job_applications = job_apps_queryset[:5] # Get latest 5

    # Get recent whitelist applications (assuming all staff can see these for now)
    # If whitelist apps also need permission checks, apply similar logic here
    recent_whitelist_applications = WhitelistApplication.objects.select_related('user').order_by('-created_at')[:5]

    context = {
        'pending_whitelist_count': pending_whitelist_count,
        'approved_whitelist_count': approved_whitelist_count,
        'rejected_whitelist_count': rejected_whitelist_count,
        'total_users': total_users,
        'pending_job_apps_count': pending_job_apps_count,
        'user_can_review_jobs': user_can_review_jobs,
        'recent_job_applications': recent_job_applications,
        'recent_whitelist_applications': recent_whitelist_applications, # Pass recent whitelist apps
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
            
            return redirect('dashboard')
    
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

@login_required
@staff_required
def logs_view(request):
    return render(request, 'dashboard/logs.html')