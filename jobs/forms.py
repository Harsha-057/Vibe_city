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
    EXPERIENCE_CHOICES = [
        ("experienced", "Experienced"),
        ("non_experienced", "Non-Experienced"),
    ]
    experience_level = forms.ChoiceField(
        label="Do you have prior law enforcement experience?",
        choices=EXPERIENCE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        help_text="Select whether you have previous law enforcement or RP experience."
    )

    # Recruit question (for non-experienced)
    recruit_reason = forms.CharField(
        label="Why do you want to join SASP?",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Briefly explain your motivation for joining SASP."
    )

    # All other SASP fields (now optional)
    irl_name = forms.CharField(label="Full Legal Name", max_length=255, required=False, help_text="Please provide your full legal name.")
    irl_age = forms.IntegerField(label="Your Age", required=False, help_text="Please provide your current age.")
    discord_name = forms.CharField(label="Discord Username & Tag", max_length=255, required=False, help_text="e.g., username#1234")
    character_backstory = forms.CharField(label="Character Backstory", widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text="Provide a detailed backstory for your character.")
    past_experience = forms.CharField(label="Relevant Experience", widget=forms.Textarea(attrs={'rows': 4}), required=False, help_text="Describe your relevant experience in law enforcement, RP, or similar fields.")
    pd_rules_vehicle_pursuit = forms.CharField(label="Vehicle Pursuit Protocols", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Explain the proper protocols for vehicle pursuits.")
    pd_rules_use_of_force = forms.CharField(label="Use of Force Continuum", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Describe your understanding of the Use of Force Continuum.")
    pd_rules_traffic_stops = forms.CharField(label="Traffic Stop Procedures", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Describe the proper procedures for traffic stops.")
    pd_rules_evidence = forms.CharField(label="Evidence Handling and Chain of Custody", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Explain the correct procedures for handling evidence.")
    pd_rules_miranda = forms.CharField(label="Miranda Rights and Arrest Procedures", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Explain Miranda rights and arrest procedures.")
    pd_rules_radio = forms.CharField(label="Radio Communication Protocols", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Explain the proper radio communication protocols.")
    pd_rules_officer_down = forms.CharField(label="Officer Down Procedures", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Describe the appropriate response when an officer is down.")
    pd_rules_scene_management = forms.CharField(label="Scene Management and Perimeter Control", widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text="Explain the steps for managing a scene and establishing a secure perimeter.")

    def clean(self):
        cleaned_data = super().clean()
        experience_level = cleaned_data.get('experience_level')
        if experience_level == 'non_experienced':
            if not cleaned_data.get('recruit_reason'):
                self.add_error('recruit_reason', 'This field is required for non-experienced applicants.')
            # Only clear detailed fields, NOT irl_name, irl_age, discord_name
            detailed_fields = [
                'character_backstory', 'past_experience',
                'pd_rules_vehicle_pursuit', 'pd_rules_use_of_force',
                'pd_rules_traffic_stops', 'pd_rules_evidence', 'pd_rules_miranda',
                'pd_rules_radio', 'pd_rules_officer_down', 'pd_rules_scene_management'
            ]
            for field in detailed_fields:
                cleaned_data[field] = ''
        elif experience_level == 'experienced':
            # Require key fields for experienced applicants
            required_fields = [
                'irl_name', 'irl_age', 'discord_name', 'character_backstory', 'past_experience'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for experienced applicants.')
        return cleaned_data

    class Meta(BaseJobApplicationForm.Meta):
        fields = BaseJobApplicationForm.Meta.fields + [
            'experience_level', 'recruit_reason',
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