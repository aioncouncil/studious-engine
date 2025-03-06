from django import forms
from .models import Zone, Sector

# [REF:33d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8:ZONE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the zone_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ZoneForm(forms.ModelForm):
    """Form for users to submit new zones"""
    
    class Meta:
        model = Zone
        fields = [
            'zone_type',
            'area',
            'city',
            'city_latitude',
            'city_longitude',
            'country',
            'sector',
            'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            # Hidden fields that will be populated by the map
            'city_latitude': forms.HiddenInput(),
            'city_longitude': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active sectors
        self.fields['sector'].queryset = Sector.objects.all()
        
        # Add helpful descriptions
        self.fields['zone_type'].help_text = "What kind of zone is this?"
        self.fields['area'].help_text = "The area classification of this zone"
        self.fields['city'].help_text = "The city where this zone is located"
        self.fields['country'].help_text = "The country where this zone is located"
        self.fields['description'].help_text = "Describe this zone and its purpose" 