from django import forms
from .models import WhitelistApplication

class WhitelistApplicationForm(forms.ModelForm):
    rules_acknowledged = forms.BooleanField(
        required=True,
        label='Do you agree to follow all rules and respect staff decisions?',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = WhitelistApplication
        fields = [
            # Discord Information
            'discord_name',
            
            # Steam Information
            'steam_name',
            'steam_hex_id',
            
            # Personal Information
            'age',
            
            # Server Information
            'fivem_experience',
            
            # Character Information
            'character_name',
            'character_age',
            
            # Roleplay Knowledge
            'rule_breaking_response',
            
            # Acknowledgment
            'rules_acknowledged'
        ]
        widgets = {
            'discord_name': forms.TextInput(attrs={'class': 'w-full'}),
            'steam_name': forms.TextInput(attrs={'class': 'w-full'}),
            'steam_hex_id': forms.TextInput(attrs={'class': 'w-full'}),
            'age': forms.NumberInput(attrs={'class': 'w-full', 'min': '16'}),
            'fivem_experience': forms.TextInput(attrs={'class': 'w-full'}),
            'character_name': forms.TextInput(attrs={'class': 'w-full'}),
            'character_age': forms.NumberInput(attrs={'class': 'w-full', 'min': '18'}),
            'rule_breaking_response': forms.Textarea(attrs={'class': 'w-full', 'rows': 3}),
        }
        labels = {
            'discord_name': 'Discord ID',
            'steam_name': 'Steam Name',
            'steam_hex_id': 'Steam Hex ID',
            'age': 'Age',
            'fivem_experience': 'How long have you been playing on FiveM?',
            'character_name': 'Character Name (First & Last)',
            'character_age': 'Character Age',
            'rule_breaking_response': 'What would you do if you saw someone breaking the rules?',
        }
        help_texts = {
            'discord_name': 'Enter your Discord name and tag (e.g., JohnDoe#1234)',
            'steam_name': 'Enter your Steam display name',
            'steam_hex_id': 'Enter your Steam Hex ID (<a href="https://steamid.pro/" target="_blank">steamid.pro</a> or <a href="https://www.steamidfinder.com/" target="_blank">steamidfinder.com</a>)',
            'age': 'You must be at least 16 years old',
            'fivem_experience': 'Describe your experience with FiveM',
            'character_name': 'Enter your character\'s full name',
            'character_age': 'Enter your character\'s age (must be 18 or older)',
            'rule_breaking_response': 'Explain how you would handle witnessing rule violations',
        }