# innovations/views.py
# This file is now deprecated in favor of the innovations/views/ package
# For compatibility, we import the views from the new module

from innovations.views.innovations import * 

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from innovations.models import Innovation

class InnovationListView(LoginRequiredMixin, ListView):
    """List all innovations."""
    model = Innovation
    template_name = 'innovations/innovation_list.html'
    context_object_name = 'innovations'
    
    def get_queryset(self):
        """Return all innovations."""
        # Get base queryset
        queryset = Innovation.objects.all()
        
        # If no innovations found in database, generate sample innovations
        if not queryset.exists():
            # Check if we need to create sample innovations
            if Innovation.objects.count() == 0:
                # Create sample innovations
                sample_innovations = [
                    {
                        'name': 'Campus Navigation App',
                        'description': 'A mobile application to help students navigate the campus efficiently.',
                        'status': 'proposed',
                        'innovation_type': 'digital',
                    },
                    {
                        'name': 'Sustainable Energy Initiative',
                        'description': 'A project to reduce campus energy usage through sustainable practices.',
                        'status': 'in_progress',
                        'innovation_type': 'sustainability',
                    },
                    {
                        'name': 'Peer Learning Network',
                        'description': 'A platform connecting students for collaborative learning and peer tutoring.',
                        'status': 'proposed',
                        'innovation_type': 'social',
                    },
                    {
                        'name': 'Smart Study Spaces',
                        'description': 'Redesigned study areas with technology integration and comfortable ergonomics.',
                        'status': 'completed',
                        'innovation_type': 'physical',
                    },
                ]
                
                for innovation_data in sample_innovations:
                    Innovation.objects.create(**innovation_data)
                
                # Refresh queryset after creating sample innovations
                queryset = Innovation.objects.all()
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context."""
        context = super().get_context_data(**kwargs)
        return context

class TechTreeView(LoginRequiredMixin, ListView):
    """Display the technology tree."""
    model = Innovation
    template_name = 'innovations/tech_tree.html'
    context_object_name = 'innovations'
    
    def get_queryset(self):
        """Return all innovations for the tech tree."""
        return Innovation.objects.all()
    
    def get_context_data(self, **kwargs):
        """Add additional context for the tech tree."""
        context = super().get_context_data(**kwargs)
        return context 