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

# --- Permission Check Functions (Updated for Boolean Fields) --- #

def is_staff(user):
    """Decorator to check if user is staff."""
    return user.is_staff

def can_review_job_application(user, application):
    """Checks if a user can review a specific application based on boolean fields."""
    if not user.is_authenticated or not user.is_staff:
        return False
    
    if user.is_superuser:
        return True

    if application.job_type == 'SASP' and user.can_review_sasp:
        return True
    elif application.job_type == 'EMS' and user.can_review_ems:
        return True
    elif application.job_type == 'MECHANIC' and user.can_review_mechanic:
        return True
    
    return False # Deny if no specific permission matches

def can_access_review_list(user):
    """Checks if a user can access the review list (has any review perm or superuser)."""
    if not user.is_authenticated or not user.is_staff:
        return False
    
    return (
        user.is_superuser or 
        user.can_review_sasp or 
        user.can_review_ems or 
        user.can_review_mechanic
    )

def can_conduct_interview(user, application):
    """Checks if a user can make hiring decisions."""
    # Simplified: For now, reuse the form review permission check
    # TODO: Implement specific fields like user.can_hire_sasp if needed
    return can_review_job_application(user, application) 

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
    # Check for existing PENDING, INTERVIEW_PENDING, HIRED, or APPROVED application for this job
    existing_app = JobApplication.objects.filter(
        applicant=request.user,
        job_type=job_type,
        status__in=['PENDING', 'INTERVIEW_PENDING', 'HIRED', 'APPROVED']
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
            # Send NEW application notification
            try:
                send_new_notification_func = import_string('discord_bot.bot.send_new_job_application_notification')
                send_new_notification_func(application)
            except Exception as e:
                messages.warning(request, f"Application submitted, but failed to send Discord notification: {e}")
                print(f"Error triggering NEW Discord notification for JobApp {application.id}: {e}")
            return redirect('profile') # Redirect to profile after success
    else:
        form = SASPApplicationForm()
    return render(request, 'jobs/sasp_apply.html', {'form': form, 'job_title': 'SASP'})

@login_required
def ems_apply_view(request):
    job_type = 'EMS'
    # Check for existing PENDING, INTERVIEW_PENDING, HIRED, or APPROVED application for this job
    existing_app = JobApplication.objects.filter(
        applicant=request.user,
        job_type=job_type,
        status__in=['PENDING', 'INTERVIEW_PENDING', 'HIRED', 'APPROVED']
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
            # Send NEW application notification
            try:
                send_new_notification_func = import_string('discord_bot.bot.send_new_job_application_notification')
                send_new_notification_func(application)
            except Exception as e:
                messages.warning(request, f"Application submitted, but failed to send Discord notification: {e}")
                print(f"Error triggering NEW Discord notification for JobApp {application.id}: {e}")
            return redirect('profile')
    else:
        form = EMSApplicationForm()
    return render(request, 'jobs/ems_apply.html', {'form': form, 'job_title': 'EMS'})

@login_required
def mechanic_apply_view(request):
    job_type = 'MECHANIC'
    # Check for existing PENDING, INTERVIEW_PENDING, HIRED, or APPROVED application for this job
    existing_app = JobApplication.objects.filter(
        applicant=request.user,
        job_type=job_type,
        status__in=['PENDING', 'INTERVIEW_PENDING', 'HIRED', 'APPROVED']
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
            # Send NEW application notification
            try:
                send_new_notification_func = import_string('discord_bot.bot.send_new_job_application_notification')
                send_new_notification_func(application)
            except Exception as e:
                messages.warning(request, f"Application submitted, but failed to send Discord notification: {e}")
                print(f"Error triggering NEW Discord notification for JobApp {application.id}: {e}")
            return redirect('profile')
    else:
        form = MechanicApplicationForm()
    return render(request, 'jobs/mechanic_apply.html', {'form': form, 'job_title': 'Mechanic'})


# --- Application Review Views (Updated for Boolean Field Checks) --- #

@method_decorator(user_passes_test(can_access_review_list), name='dispatch')
class JobApplicationReviewListView(ListView):
    model = JobApplication
    template_name = 'jobs/jobapplication_list.html' 
    context_object_name = 'applications' 
    paginate_by = 20

    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'PENDING')
        job_type_filter = self.request.GET.get('job_type', '') 

        queryset = JobApplication.objects.select_related('applicant').order_by('-submitted_at')
        
        # Filter by Job Type user is allowed to review (if not superuser)
        if not self.request.user.is_superuser:
            allowed_job_types = []
            if self.request.user.can_review_sasp: allowed_job_types.append('SASP')
            if self.request.user.can_review_ems: allowed_job_types.append('EMS')
            if self.request.user.can_review_mechanic: allowed_job_types.append('MECHANIC')
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
        # Use field.choices to get value/display pairs correctly
        all_choices_dict = dict(JobApplication._meta.get_field('job_type').choices)
        
        if self.request.user.is_superuser or self.request.user.can_review_sasp:
             allowed_job_types_choices.append(('SASP', all_choices_dict.get('SASP', 'SASP')))
        if self.request.user.is_superuser or self.request.user.can_review_ems:
             allowed_job_types_choices.append(('EMS', all_choices_dict.get('EMS', 'EMS')))
        if self.request.user.is_superuser or self.request.user.can_review_mechanic:
             allowed_job_types_choices.append(('MECHANIC', all_choices_dict.get('MECHANIC', 'Mechanic')))
        
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
        # Perform permission checks
        self.user_can_review = can_review_job_application(request.user, application_obj)
        self.user_can_hire = can_conduct_interview(request.user, application_obj)

        if not self.user_can_review:
            messages.error(request, "You do not have permission to view this application.")
            return redirect('job_application_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass permission results to the template
        context['user_can_review'] = getattr(self, 'user_can_review', False)
        context['user_can_hire'] = getattr(self, 'user_can_hire', False)
        return context

    def get_queryset(self):
        # Renamed reviewer field, update select_related if needed
        return super().get_queryset().select_related('applicant', 'form_reviewer', 'interview_reviewer')


@login_required
def update_job_application_status(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    current_status = application.status
    user_can_review_form = can_review_job_application(request.user, application)
    user_can_hire = can_conduct_interview(request.user, application) # Check hiring permission

    if request.method == 'POST':
        action = request.POST.get('action') # Use 'action' instead of 'status' for clarity
        feedback_text = request.POST.get('feedback', '').strip()

        if current_status == 'PENDING' and user_can_review_form:
            if action == 'APPROVE_FORM':
                application.status = 'INTERVIEW_PENDING'
                application.form_reviewer = request.user
                application.form_reviewed_at = timezone.now()
                application.form_feedback = feedback_text
                application.save()
                messages.success(request, "Application form approved. Status set to Pending Interview.")
                # Send notification for interview pending
                try:
                    send_notification_func = import_string('discord_bot.bot.send_job_application_result')
                    send_notification_func(application)
                except Exception as e:
                    messages.error(request, f"Failed to send Discord notification: {e}")
                    print(f"Error triggering Discord notification for JobApp {pk}: {e}")
            elif action == 'REJECT_FORM':
                application.status = 'REJECTED'
                application.form_reviewer = request.user
                application.form_reviewed_at = timezone.now()
                application.form_feedback = feedback_text
                application.save()
                messages.success(request, "Application form rejected.")
                # Send notification (using renamed feedback field)
                try:
                    send_notification_func = import_string('discord_bot.bot.send_job_application_result')
                    send_notification_func(application)
                except Exception as e:
                    messages.error(request, f"Failed to send Discord notification: {e}")
                    print(f"Error triggering Discord notification for JobApp {pk}: {e}")
            else:
                messages.error(request, "Invalid action for current status.")
        
        elif current_status == 'INTERVIEW_PENDING' and user_can_hire:
            if action == 'HIRE':
                application.status = 'HIRED'
                application.interview_reviewer = request.user
                application.interview_reviewed_at = timezone.now()
                application.interview_feedback = feedback_text
                application.save()
                
                # Update user's employment status
                hired_user = application.applicant
                if application.job_type == 'SASP':
                    hired_user.is_sasp_employee = True
                elif application.job_type == 'EMS':
                    hired_user.is_ems_employee = True
                elif application.job_type == 'MECHANIC':
                    hired_user.is_mechanic_employee = True
                hired_user.save()
                
                messages.success(request, "Applicant Hired!")
                # TODO: Assign job role/tag in Discord?
                # Send notification
                try:
                    send_notification_func = import_string('discord_bot.bot.send_job_application_result')
                    send_notification_func(application)
                except Exception as e:
                    messages.error(request, f"Failed to send Discord notification: {e}")
                    print(f"Error triggering Discord notification for JobApp {pk}: {e}")
            elif action == 'REJECT_INTERVIEW':
                application.status = 'REJECTED_INTERVIEW'
                application.interview_reviewer = request.user
                application.interview_reviewed_at = timezone.now()
                application.interview_feedback = feedback_text
                application.save()
                messages.success(request, "Applicant Rejected after interview.")
                # Send notification
                try:
                    send_notification_func = import_string('discord_bot.bot.send_job_application_result')
                    send_notification_func(application)
                except Exception as e:
                    messages.error(request, f"Failed to send Discord notification: {e}")
                    print(f"Error triggering Discord notification for JobApp {pk}: {e}")
            else:
                messages.error(request, "Invalid action for current status.")

        else:
            # Handle cases where user doesn't have permission or status isn't actionable
            if not user_can_review_form and not user_can_hire:
                 messages.error(request, "You do not have permission to update this application's status.")
            else:
                 messages.warning(request, f"No action taken. Application status is currently '{application.get_status_display()}' or you lack permission for this stage.")
        
        return redirect('job_application_detail', pk=pk)
    else:
        # GET request, just redirect back
        return redirect('job_application_detail', pk=pk)
