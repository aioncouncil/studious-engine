from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib import messages
from django.http import JsonResponse

# Temporary stub models
class MockTechNode:
    def __init__(self, id):
        self.id = id
        self.name = f"Tech {id}"
        self.description = f"Detailed description for Tech {id}"
        self.level = id % 3 + 1
        self.unlocked = id < 3
        
        self.prerequisites = [
            {
                'id': id - 1,
                'name': f'Tech {id - 1}',
                'unlocked': True
            }
        ] if id > 1 else []
        
        self.unlocks = [
            {
                'id': id + 2,
                'name': f'Tech {id + 2}',
                'unlocked': False
            }
        ] if id < 5 else []
        
        self.related_innovations = [
            {
                'id': i,
                'name': f'Innovation {i}',
                'current_stage': 'implementation' if i % 2 == 0 else 'testing'
            } for i in range(id, id + 2)
        ]


class MockInnovation:
    def __init__(self, innovation_id):
        stage = innovation_id % 3
        stages = {0: 'ideation', 1: 'implementation', 2: 'testing'}
        stage_display = {0: 'Ideation', 1: 'Implementation', 2: 'Testing'}
        
        self.id = innovation_id
        self.name = f"Innovation {innovation_id}"
        self.description = "This is a stub innovation for development testing."
        self.current_stage = stages[stage]
        self.progress = 25 * (innovation_id % 4)
        self.zone_id = innovation_id * 10
        
        class Zone:
            # Create a local zone_id to avoid naming conflict with built-in id() function
            zone_id = innovation_id * 10
            id = zone_id  # Assign the computed value to id
            zone_number = innovation_id
            zone_type = f"Zone Type {innovation_id}"
            
            class Sector:
                sector_id = innovation_id
                id = sector_id  # Assign the computed value to id
                name = f"Sector {innovation_id}"
            
            sector = Sector()
        
        self.zone = Zone()
        self._stage_display = stage_display[stage]
    
    def get_current_stage_display(self):
        return self._stage_display


class InnovationListView(LoginRequiredMixin, ListView):
    """List all innovation projects on campus."""
    template_name = 'innovations/innovation_list.html'
    context_object_name = 'innovations'
    
    def get_queryset(self):
        return [MockInnovation(i) for i in range(1, 5)]


class InnovationDetailView(LoginRequiredMixin, DetailView):
    """Show details of a specific innovation."""
    template_name = 'innovations/innovation_detail.html'
    context_object_name = 'innovation'
    
    def get_object(self, queryset=None):
        # Stub implementation
        innovation_id = self.kwargs.get('pk')
        return MockInnovation(innovation_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stub implementation of additional context
        context.update({
            'contributors': [
                {
                    'player': {
                        'user': {
                            'username': f'Player{i}'
                        }
                    },
                    'contribution_points': 50 - (i * 7),
                    'contribution_date': f'2023-0{i}-01'
                } for i in range(1, 5)
            ],
            'documents': [
                {
                    'id': i,
                    'title': f'Document {i}',
                    'description': f'Description for Document {i}',
                    'uploaded_by': f'Player{i}',
                    'uploaded_at': f'2023-0{i}-01'
                } for i in range(1, 3)
            ],
            'comments': [
                {
                    'id': i,
                    'text': f'This is comment {i} on the innovation.',
                    'author': f'Player{i}',
                    'created_at': f'2023-0{i}-01'
                } for i in range(1, 4)
            ],
            'player_contribution': {
                'contribution_points': 35,
                'last_contributed': '2023-05-01'
            }
        })
        
        return context


class InnovationCreateView(LoginRequiredMixin, CreateView):
    """Create a new innovation."""
    template_name = 'innovations/innovation_create.html'
    
    def get(self, request, *args, **kwargs):
        # Stub implementation
        return render(request, self.template_name, {
            'zones': [
                {'id': i * 10, 'name': f'Zone {i}', 'sector': f'Sector {i}'} 
                for i in range(1, 4)
            ]
        })
    
    def post(self, request, *args, **kwargs):
        # Stub implementation - would create innovation in real app
        return redirect('innovations:innovation_list')


class InnovationContributeView(LoginRequiredMixin, UpdateView):
    """Contribute to an existing innovation."""
    template_name = 'innovations/innovation_contribute.html'
    
    def get(self, request, *args, **kwargs):
        # Stub implementation
        innovation_id = self.kwargs.get('pk')
        return render(request, self.template_name, {
            'innovation': MockInnovation(innovation_id),
            'contribution_types': [
                {'id': 1, 'name': 'Document Upload', 'description': 'Upload a document related to this innovation'},
                {'id': 2, 'name': 'Comment', 'description': 'Leave a comment or suggestion'},
                {'id': 3, 'name': 'Development Work', 'description': 'Contribute code or development work'}
            ]
        })
    
    def post(self, request, *args, **kwargs):
        # Stub implementation - would process contribution in real app
        return redirect('innovations:innovation_detail', pk=self.kwargs.get('pk'))


class TechTreeView(LoginRequiredMixin, TemplateView):
    """Display the technology tree for the game."""
    template_name = 'innovations/tech_tree.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stub implementation
        context.update({
            'tech_tree_nodes': [
                {
                    'id': i,
                    'name': f'Tech {i}',
                    'description': f'Description for Tech {i}',
                    'level': i % 3 + 1,
                    'unlocked': i < 3,
                    'children': [i+3, i+4] if i < 3 else []
                } for i in range(1, 7)
            ]
        })
        
        return context


class TechTreeNodeDetailView(LoginRequiredMixin, DetailView):
    """Show details of a specific tech tree node."""
    template_name = 'innovations/tech_node_detail.html'
    context_object_name = 'node'
    
    def get_object(self, queryset=None):
        # Stub implementation
        node_id = self.kwargs.get('pk')
        return MockTechNode(node_id) 