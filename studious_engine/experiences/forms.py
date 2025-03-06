from django import forms
from .models import Experience

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ExperienceForm(forms.ModelForm):
    """Form for users to submit new experiences"""
    
    class Meta:
        model = Experience
        fields = [
            'name', 
            'description',
            'experience_type',
            'difficulty',
            'duration_minutes',
            'latitude', 
            'longitude',
            'associated_zones',
            # Simplified fields for user submission
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            # Hidden fields that will be populated by the map
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional for user-friendliness
        self.fields['associated_zones'].required = False
        
        # Add helpful descriptions
        self.fields['name'].help_text = "Give your experience a catchy, descriptive name"
        self.fields['description'].help_text = "Describe what participants will do in this experience"
        self.fields['difficulty'].help_text = "Rate from 1 (easiest) to 10 (hardest)"
        self.fields['duration_minutes'].help_text = "Estimated time to complete in minutes" 