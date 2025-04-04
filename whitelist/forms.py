from django import forms
from .models import WhitelistApplication

class WhitelistApplicationForm(forms.ModelForm):
    rules_acknowledged = forms.BooleanField(
        required=True,
        label='I have read and understand the server rules',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = WhitelistApplication
        fields = [
            # User Information
            'your_name',
            'your_age',
            'your_gender',
            'discord_name',
            # Character Information
            'character_name',
            'character_gender',
            'character_age',
            # Acknowledgment
            'rules_acknowledged'
        ]
        widgets = {
            'your_name': forms.TextInput(attrs={'class': 'w-full'}),
            'your_age': forms.NumberInput(attrs={'class': 'w-full', 'min': '16'}),
            'your_gender': forms.Select(attrs={'class': 'w-full'}),
            'discord_name': forms.TextInput(attrs={'class': 'w-full'}),
            'character_name': forms.TextInput(attrs={'class': 'w-full'}),
            'character_gender': forms.Select(attrs={'class': 'w-full'}),
            'character_age': forms.NumberInput(attrs={'class': 'w-full', 'min': '18'}),
        }
        labels = {
            'your_name': 'Your Name',
            'your_age': 'Your Age',
            'your_gender': 'Your Gender',
            'discord_name': 'Discord Username',
            'character_name': 'Character Name',
            'character_gender': 'Character Gender',
            'character_age': 'Character Age',
        }
        help_texts = {
            'your_name': 'Enter your real name',
            'your_age': 'You must be at least 16 years old',
            'your_gender': 'Select your gender',
            'discord_name': 'Enter your Discord username (e.g., username#1234)',
            'character_name': 'Enter your character\'s name',
            'character_gender': 'Select your character\'s gender',
            'character_age': 'Enter your character\'s age (must be 18 or older)',
        }