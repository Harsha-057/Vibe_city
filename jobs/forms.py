from django import forms
from .models import JobApplication

class BaseJobApplicationForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = JobApplication
        fields = ['character_name', 'date_of_birth', 'previous_experience', 'reason']
        widgets = {
            'previous_experience': forms.Textarea(attrs={'rows': 4}),
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'date_of_birth': 'In-game character date of birth.',
            'previous_experience': 'Describe any relevant previous experience (optional).',
            'reason': 'Why are you applying for this position?',
        }

class SASPApplicationForm(BaseJobApplicationForm):
    sasp_scenario_response = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, help_text="Describe how you would handle a specific scenario (e.g., a high-speed pursuit ending in a crash).")
    sasp_leadership_experience = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Describe any relevant leadership experience.")

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + ['sasp_scenario_response', 'sasp_leadership_experience']

class EMSApplicationForm(BaseJobApplicationForm):
    ems_medical_certification = forms.CharField(max_length=255, required=False, help_text="List any relevant medical certifications (e.g., EMT, Paramedic)." )
    ems_pressure_handling = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, help_text="Describe how you handle high-pressure situations.")

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + ['ems_medical_certification', 'ems_pressure_handling']

class MechanicApplicationForm(BaseJobApplicationForm):
    mechanic_skills = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, help_text="List your relevant mechanical skills and experience (e.g., engine repair, tuning, bodywork).")
    mechanic_tool_knowledge = forms.BooleanField(required=False, help_text="Do you own or have extensive knowledge of specialized mechanic tools?")

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + ['mechanic_skills', 'mechanic_tool_knowledge'] 