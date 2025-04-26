from django.urls import path
from . import views

urlpatterns = [
    # Public job pages
    path('', views.AvailableJobsView.as_view(), name='available_jobs'),
    path('apply/', views.JobListView.as_view(), name='job_list'),

    # Specific application forms
    path('sasp/apply/', views.sasp_apply_view, name='sasp_apply'),
    path('ems/apply/', views.ems_apply_view, name='ems_apply'),
    path('mechanic/apply/', views.mechanic_apply_view, name='mechanic_apply'),

    # Staff review views
    path('review/', views.JobApplicationReviewListView.as_view(), name='job_application_list'),
    path('review/<int:pk>/', views.JobApplicationReviewDetailView.as_view(), name='job_application_detail'),
    path('review/<int:pk>/update_status/', views.update_job_application_status, name='update_job_application_status'),

    path('fire/<int:user_id>/', views.fire_employee_view, name='fire_employee'),
] 