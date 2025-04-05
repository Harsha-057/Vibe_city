from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import Group
from django.utils.module_loading import import_string

from .models import JobApplication
from .forms import SASPApplicationForm, EMSApplicationForm, MechanicApplicationForm

# --- Permission Check Functions --- #

def is_staff(user):
    """Decorator to check if user is staff."""
    return user.is_staff

def can_review_job_application(user, application):
    """Checks if a user can review a specific application based on group membership."""
    if not user.is_authenticated or not user.is_staff:
        return False
    
    required_group_name = None
    if application.job_type == 'SASP':
        required_group_name = "SASP Reviewers"
    elif application.job_type == 'EMS':
        required_group_name = "EMS Reviewers"
    elif application.job_type == 'MECHANIC':
        required_group_name = "Mechanic Reviewers"
    
    if required_group_name:
        return user.groups.filter(name=required_group_name).exists() or user.is_superuser
    
    return user.is_superuser

def can_access_review_list(user):
    """Checks if a user can access the review list (in any reviewer group or superuser)."""
    if not user.is_authenticated or not user.is_staff:
        return False
    reviewer_groups = ["SASP Reviewers", "EMS Reviewers", "Mechanic Reviewers"]
    return user.groups.filter(name__in=reviewer_groups).exists() or user.is_superuser

# --- Public Views --- #

# View for the page listing available jobs descriptions/links
class AvailableJobsView(TemplateView):
    template_name = "jobs/available_jobs.html"

# View to list application links (kept for potential direct access if needed)
class JobListView(ListView):
    model = JobApplication
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return []

# --- Specific Application Form Views --- #

@login_required
def sasp_apply_view(request):
    job_type = 'SASP'
    # Check for existing PENDING or APPROVED application for this job
    existing_app = JobApplication.objects.filter(
        applicant=request.user, 
        job_type=job_type, 
        status__in=['PENDING', 'APPROVED']
    ).first()

    if existing_app:
        messages.warning(request, f"You already have a {existing_app.get_status_display().lower()} application for {existing_app.get_job_type_display()}. You cannot apply again at this time.")
        return redirect('profile') # Redirect to profile where they can see status

    if request.method == 'POST':
        form = SASPApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job_type = job_type
            application.save()
            messages.success(request, 'SASP application submitted successfully!')
            return redirect('profile') # Redirect to profile after success
    else:
        form = SASPApplicationForm()
    return render(request, 'jobs/sasp_apply.html', {'form': form, 'job_title': 'SASP'})

@login_required
def ems_apply_view(request):
    job_type = 'EMS'
    existing_app = JobApplication.objects.filter(
        applicant=request.user, 
        job_type=job_type, 
        status__in=['PENDING', 'APPROVED']
    ).first()

    if existing_app:
        messages.warning(request, f"You already have a {existing_app.get_status_display().lower()} application for {existing_app.get_job_type_display()}. You cannot apply again at this time.")
        return redirect('profile')

    if request.method == 'POST':
        form = EMSApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job_type = job_type
            application.save()
            messages.success(request, 'EMS application submitted successfully!')
            return redirect('profile')
    else:
        form = EMSApplicationForm()
    return render(request, 'jobs/ems_apply.html', {'form': form, 'job_title': 'EMS'})

@login_required
def mechanic_apply_view(request):
    job_type = 'MECHANIC'
    existing_app = JobApplication.objects.filter(
        applicant=request.user, 
        job_type=job_type, 
        status__in=['PENDING', 'APPROVED']
    ).first()

    if existing_app:
        messages.warning(request, f"You already have a {existing_app.get_status_display().lower()} application for {existing_app.get_job_type_display()}. You cannot apply again at this time.")
        return redirect('profile')

    if request.method == 'POST':
        form = MechanicApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.job_type = job_type
            application.save()
            messages.success(request, 'Mechanic application submitted successfully!')
            return redirect('profile')
    else:
        form = MechanicApplicationForm()
    return render(request, 'jobs/mechanic_apply.html', {'form': form, 'job_title': 'Mechanic'})


# --- Application Review Views --- #

@method_decorator(user_passes_test(can_access_review_list), name='dispatch')
class JobApplicationReviewListView(ListView):
    model = JobApplication
    template_name = 'jobs/jobapplication_list.html' 
    context_object_name = 'applications' 
    paginate_by = 20

    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'PENDING')
        job_type_filter = self.request.GET.get('job_type', '') # Get job_type filter

        queryset = JobApplication.objects.select_related('applicant').order_by('-submitted_at')
        
        # Filter by Job Type user is allowed to review (if not superuser)
        if not self.request.user.is_superuser:
            allowed_job_types = []
            if self.request.user.groups.filter(name="SASP Reviewers").exists():
                allowed_job_types.append('SASP')
            if self.request.user.groups.filter(name="EMS Reviewers").exists():
                allowed_job_types.append('EMS')
            if self.request.user.groups.filter(name="Mechanic Reviewers").exists():
                allowed_job_types.append('MECHANIC')
            queryset = queryset.filter(job_type__in=allowed_job_types)
        
        # Apply explicit filters from GET params
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if job_type_filter:
            queryset = queryset.filter(job_type=job_type_filter)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = JobApplication.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', 'PENDING')
        
        # Get job types the user can review for the filter dropdown
        allowed_job_types_choices = []
        if self.request.user.is_superuser:
            allowed_job_types_choices = JobApplication.JOB_CHOICES
        else:
            if self.request.user.groups.filter(name="SASP Reviewers").exists():
                 allowed_job_types_choices.append(('SASP', JobApplication._meta.get_field('job_type').choices[0][1])) # Get display name
            if self.request.user.groups.filter(name="EMS Reviewers").exists():
                 allowed_job_types_choices.append(('EMS', JobApplication._meta.get_field('job_type').choices[1][1]))
            if self.request.user.groups.filter(name="Mechanic Reviewers").exists():
                 allowed_job_types_choices.append(('MECHANIC', JobApplication._meta.get_field('job_type').choices[2][1]))
        
        context['job_type_choices'] = allowed_job_types_choices
        context['current_job_type'] = self.request.GET.get('job_type', '')
        return context


@method_decorator(login_required, name='dispatch')
class JobApplicationReviewDetailView(DetailView):
    model = JobApplication
    template_name = 'jobs/jobapplication_detail.html'
    context_object_name = 'application'

    def dispatch(self, request, *args, **kwargs):
        application_obj = self.get_object()
        if not can_review_job_application(request.user, application_obj):
            messages.error(request, "You do not have permission to view this application.")
            return redirect('job_application_list')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().select_related('applicant', 'reviewer')


@login_required
def update_job_application_status(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if not can_review_job_application(request.user, application):
         messages.error(request, "You do not have permission to update this application's status.")
         return redirect('job_application_detail', pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        feedback_text = request.POST.get('feedback', '').strip()
        if new_status in ['APPROVED', 'REJECTED']:
            application.status = new_status
            application.reviewer = request.user
            application.reviewed_at = timezone.now()
            application.feedback = feedback_text
            application.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}. Feedback saved.')
            try:
                send_notification_func = import_string('discord_bot.bot.send_job_application_result')
                send_notification_func(application)
            except Exception as e:
                messages.error(request, f"Failed to send Discord notification: {e}")
                print(f"Error triggering Discord notification for JobApp {pk}: {e}")
        else:
            messages.error(request, 'Invalid status provided.')
        return redirect('job_application_detail', pk=pk)
    else:
        return redirect('job_application_detail', pk=pk)
