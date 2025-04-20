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
            'how_found',
            'fivem_experience',
            
            # Character Information
            'character_name',
            'character_age',
            'character_backstory',
            
            # Roleplay Knowledge
            'fear_rp_explanation',
            'fail_rp_explanation',
            'robbery_response',
            'rule_breaking_response',
            
            # Acknowledgment
            'rules_acknowledged'
        ]
        widgets = {
            'discord_name': forms.TextInput(attrs={'class': 'w-full'}),
            'steam_name': forms.TextInput(attrs={'class': 'w-full'}),
            'steam_hex_id': forms.TextInput(attrs={'class': 'w-full'}),
            'age': forms.NumberInput(attrs={'class': 'w-full', 'min': '16'}),
            'how_found': forms.TextInput(attrs={'class': 'w-full'}),
            'fivem_experience': forms.TextInput(attrs={'class': 'w-full'}),
            'character_name': forms.TextInput(attrs={'class': 'w-full'}),
            'character_age': forms.NumberInput(attrs={'class': 'w-full', 'min': '18'}),
            'character_backstory': forms.Textarea(attrs={'class': 'w-full', 'rows': 5}),
            'fear_rp_explanation': forms.Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'fail_rp_explanation': forms.Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'robbery_response': forms.Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'rule_breaking_response': forms.Textarea(attrs={'class': 'w-full', 'rows': 3}),
        }
        labels = {
            'discord_name': 'Discord Name & Tag',
            'steam_name': 'Steam Name',
            'steam_hex_id': 'Steam Hex ID',
            'age': 'Age',
            'how_found': 'How did you find our server?',
            'fivem_experience': 'How long have you been playing on FiveM?',
            'character_name': 'Character Name (First & Last)',
            'character_age': 'Character Age',
            'character_backstory': 'Character Backstory',
            'fear_rp_explanation': 'What is FearRP?',
            'fail_rp_explanation': 'What is FailRP? Give an example.',
            'robbery_response': 'You\'re being robbed at gunpoint. What do you do, and what should your character value?',
            'rule_breaking_response': 'What would you do if you saw someone breaking the rules?',
        }
        help_texts = {
            'discord_name': 'Enter your Discord name and tag (e.g., JohnDoe#1234)',
            'steam_name': 'Enter your Steam display name',
            'steam_hex_id': 'Enter your Steam Hex ID',
            'age': 'You must be at least 16 years old',
            'how_found': 'Tell us how you discovered our server',
            'fivem_experience': 'Describe your experience with FiveM',
            'character_name': 'Enter your character\'s full name',
            'character_age': 'Enter your character\'s age (must be 18 or older)',
            'character_backstory': 'Write a detailed backstory for your character (minimum 5 sentences)',
            'fear_rp_explanation': 'Explain what FearRP means in roleplay',
            'fail_rp_explanation': 'Explain what FailRP is and provide an example',
            'robbery_response': 'Describe how your character would react to being robbed at gunpoint',
            'rule_breaking_response': 'Explain how you would handle witnessing rule violations',
        }