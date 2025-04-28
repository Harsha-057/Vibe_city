from django import forms
from .models import JobApplication

class BaseJobApplicationForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = JobApplication
        fields = ['character_name', 'date_of_birth', 'reason']
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
    irl_name = forms.CharField(max_length=255, required=True, help_text="Please provide your full legal name")
    irl_age = forms.IntegerField(required=True, help_text="Please provide your current age")
    discord_name = forms.CharField(max_length=255, required=True, help_text="Please provide your Discord username and tag (e.g., username#1234)")
    character_backstory = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}), 
        required=True, 
        help_text="Please provide a detailed backstory for your character, including their background, motivations, and any relevant life experiences"
    )
    past_experience = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}), 
        required=True, 
        help_text="Please describe your relevant experience in law enforcement, roleplay, or similar fields"
    )
    
    # PD Rules Questions
    pd_rules_vehicle_pursuit = forms.CharField(
        label="Vehicle Pursuit Protocols",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please explain the proper protocols for initiating, conducting, and terminating vehicle pursuits."
    )
    pd_rules_use_of_force = forms.CharField(
        label="Use of Force Continuum",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please describe your understanding of the Use of Force Continuum and when each level of force is appropriate."
    )
    pd_rules_traffic_stops = forms.CharField(
        label="Traffic Stop Procedures",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please describe the proper procedures for conducting traffic stops and maintaining officer safety."
    )
    pd_rules_evidence = forms.CharField(
        label="Evidence Handling and Chain of Custody",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please explain the correct procedures for handling, collecting, and maintaining the chain of custody for evidence."
    )
    pd_rules_miranda = forms.CharField(
        label="Miranda Rights and Arrest Procedures",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please describe when and how Miranda rights should be given and the proper procedures for making an arrest."
    )
    pd_rules_radio = forms.CharField(
        label="Radio Communication Protocols",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please explain the proper protocols for radio communication during police operations."
    )
    pd_rules_officer_down = forms.CharField(
        label="Officer Down Procedures",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please describe the appropriate response and procedures when an officer is down."
    )
    pd_rules_scene_management = forms.CharField(
        label="Scene Management and Perimeter Control",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Please explain the steps for managing a crime or incident scene and establishing a secure perimeter."
    )

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + [
            'irl_name', 'irl_age', 'discord_name', 'character_backstory', 'past_experience',
            'pd_rules_vehicle_pursuit', 'pd_rules_use_of_force', 'pd_rules_traffic_stops',
            'pd_rules_evidence', 'pd_rules_miranda', 'pd_rules_radio',
            'pd_rules_officer_down', 'pd_rules_scene_management'
        ]

class EMSApplicationForm(BaseJobApplicationForm):
    ems_interest = forms.CharField(
        label="Why Do You Want to Join EMS?",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Please explain your motivation for joining the EMS team."
    )
    ems_qualities = forms.CharField(
        label="Qualities of a Good EMS Worker",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="What qualities do you think are important for someone working in EMS?"
    )
    ems_helped_someone = forms.CharField(
        label="Helping in a Stressful Situation",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Describe a time when you helped someone in a stressful or emergency situation."
    )
    ems_pressure_handling = forms.CharField(
        label="Handling High-Pressure Situations",
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True,
        help_text="Please describe how you handle high-pressure or emergency situations."
    )

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + [
            'ems_interest', 'ems_qualities', 'ems_helped_someone', 'ems_pressure_handling'
        ]

class MechanicApplicationForm(BaseJobApplicationForm):
    mechanic_skills = forms.CharField(
        label="Mechanical Skills and Experience",
        widget=forms.Textarea(attrs={'rows': 4}),
        required=True,
        help_text="Please list your relevant mechanical skills and experience (e.g., engine repair, diagnostics, tuning, bodywork)."
    )
    mechanic_tool_knowledge = forms.CharField(
        label="Familiarity with Specialized Tools",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Are you familiar with or do you own any specialized mechanic tools? Please describe."
    )
    mechanic_problem_solving = forms.CharField(
        label="Problem-Solving Example",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Describe a time when you solved a difficult mechanical problem."
    )
    mechanic_interest = forms.CharField(
        label="Interest in Working as a Mechanic",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Why are you interested in working as a mechanic in our community?"
    )

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + [
            'mechanic_skills', 'mechanic_tool_knowledge', 'mechanic_problem_solving', 'mechanic_interest'
        ] 