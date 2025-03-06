# studious_engine/experiences/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import transaction

# Corrected import path for PlayerProfile
# from studious_engine.core.models import PlayerProfile

# Temporary stub models
class MockPlayer:
    def __init__(self):
        pass

# Import the models
from experiences.models import (
    Experience, PlayerExperience, Power, PlayerPower,
    ExperienceInstance, ExperienceParticipation
)
from core.models import PlayerProfile
from zones.models import Zone
from .forms import ExperienceForm  # We'll create this form

# [REF:22c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7:EXPERIENCE_SYSTEM]
# [CLAUDE:CHECK_PATTERN:matrix_flow]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:CHECK_PATTERN:zone_geographic_patterns]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the experience_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

class ExperienceListView(LoginRequiredMixin, ListView):
    """List all available experiences."""
    template_name = 'experiences/experience_list.html'
    context_object_name = 'experiences'
    
    def get_queryset(self):
        """Return all active experiences that meet the player's rank"""
        # Get filter parameters
        experience_type = self.request.GET.get('type')
        matrix_position = self.request.GET.get('matrix')
        zone_id = self.request.GET.get('zone')
        min_level = self.request.GET.get('level', 1)
        
        # Base queryset: active experiences
        queryset = Experience.objects.filter(is_active=True)
        
        # Apply filters if provided
        if experience_type:
            queryset = queryset.filter(experience_type=experience_type)
        
        if matrix_position:
            queryset = queryset.filter(matrix_position=matrix_position)
        
        if zone_id:
            queryset = queryset.filter(associated_zones__id=zone_id)
        
        if min_level:
            try:
                min_level = int(min_level)
                queryset = queryset.filter(minimum_rank__lte=min_level)
            except (ValueError, TypeError):
                pass
        
        # Filter out experiences the player has already started or completed
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            player_experience_ids = player.experiences.values_list('experience_id', flat=True)
            queryset = queryset.exclude(id__in=player_experience_ids)
        except PlayerProfile.DoesNotExist:
            # If player profile doesn't exist, don't apply this filter
            pass
            
        # If no experiences found in database, generate some sample experiences
        if not queryset.exists():
            from django.utils import timezone
            
            # Check if we need to create sample experiences
            if Experience.objects.count() == 0:
                # Create sample experiences
                sample_experiences = [
                    {
                        'name': 'Campus Tour Challenge',
                        'description': 'Explore key locations on campus and document your findings. Great for new students!',
                        'experience_type': 'challenge',
                        'matrix_position': 'body_out',
                        'art_type': 'usage',
                        'good_type': 'present',
                        'difficulty': 3,
                        'duration_minutes': 60,
                        'happiness_reward': 20,
                        'experience_reward': 100,
                        'definition': 'A guided exploration of campus landmarks',
                        'end': 'To familiarize students with campus layout',
                        'parts': 'Map reading, photo documentation, checkpoint visits',
                        'matter': 'Campus map, smartphone, comfortable walking shoes',
                        'instrument': 'EudaimoniaGo app, camera',
                        'is_active': True,
                        'minimum_rank': 1,
                    },
                    {
                        'name': 'Student Mentorship Program',
                        'description': 'Connect with a junior student and help them navigate academic challenges',
                        'experience_type': 'collaboration',
                        'matrix_position': 'soul_in',
                        'art_type': 'production',
                        'good_type': 'present_future',
                        'difficulty': 5,
                        'duration_minutes': 120,
                        'happiness_reward': 35,
                        'experience_reward': 200,
                        'definition': 'A peer-to-peer mentorship opportunity',
                        'end': 'To develop leadership skills and support junior students',
                        'parts': 'Weekly meetings, goal setting, progress tracking',
                        'matter': 'Mentorship guidelines, academic resources',
                        'instrument': 'Communication platforms, shared calendar',
                        'is_active': True,
                        'minimum_rank': 2,
                    },
                    {
                        'name': 'Campus Sustainability Quest',
                        'description': 'Identify opportunities to improve campus sustainability and implement a small-scale solution',
                        'experience_type': 'quest',
                        'matrix_position': 'body_in',
                        'art_type': 'production',
                        'good_type': 'future',
                        'difficulty': 7,
                        'duration_minutes': 180,
                        'happiness_reward': 50,
                        'experience_reward': 350,
                        'definition': 'A sustainability initiative design and implementation',
                        'end': 'To promote environmental awareness and action',
                        'parts': 'Problem identification, solution design, implementation, impact measurement',
                        'matter': 'Sustainability resources, project materials',
                        'instrument': 'Project management tools, data collection methods',
                        'is_active': True,
                        'minimum_rank': 2,
                    },
                    {
                        'name': 'Academic Research Innovation',
                        'description': 'Work with a faculty member to contribute to ongoing research in your field of interest',
                        'experience_type': 'innovation',
                        'matrix_position': 'soul_out',
                        'art_type': 'imitation',
                        'good_type': 'future',
                        'difficulty': 8,
                        'duration_minutes': 240,
                        'happiness_reward': 70,
                        'experience_reward': 500,
                        'definition': 'A research assistantship opportunity',
                        'end': 'To gain research experience and contribute to academic knowledge',
                        'parts': 'Literature review, data collection, analysis, reporting',
                        'matter': 'Academic databases, research protocols',
                        'instrument': 'Research software, analytical tools',
                        'is_active': True,
                        'minimum_rank': 3,
                    },
                    {
                        'name': 'Personal Growth Reflection',
                        'description': 'Document and analyze your personal growth journey this semester',
                        'experience_type': 'reflection',
                        'matrix_position': 'soul_in',
                        'art_type': 'usage',
                        'good_type': 'present_future',
                        'difficulty': 4,
                        'duration_minutes': 90,
                        'happiness_reward': 40,
                        'experience_reward': 150,
                        'definition': 'A structured self-reflection exercise',
                        'end': 'To develop self-awareness and set future goals',
                        'parts': 'Journaling, goal review, milestone identification',
                        'matter': 'Past assessments, personal journal',
                        'instrument': 'Reflection frameworks, goal-setting templates',
                        'is_active': True,
                        'minimum_rank': 1,
                    },
                ]
                
                for exp_data in sample_experiences:
                    Experience.objects.create(**exp_data)
                
                # Refresh queryset after creating sample experiences
                queryset = Experience.objects.filter(is_active=True)
                
                if experience_type:
                    queryset = queryset.filter(experience_type=experience_type)
                
                if matrix_position:
                    queryset = queryset.filter(matrix_position=matrix_position)
                
                if min_level:
                    try:
                        min_level = int(min_level)
                        queryset = queryset.filter(minimum_rank__lte=min_level)
                    except (ValueError, TypeError):
                        pass
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add active experiences and zones to context"""
        context = super().get_context_data(**kwargs)
        
        # Add active experiences (those the player has already started)
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            context['active_experiences'] = PlayerExperience.objects.filter(
                player=player
            ).exclude(
                status='completed'
            ).exclude(
                status='abandoned'
            )
        except PlayerProfile.DoesNotExist:
            context['active_experiences'] = []
            
        # Add zones for filtering
        context['zones'] = Zone.objects.all()
        
        return context


class ExperienceDetailView(LoginRequiredMixin, DetailView):
    """Show details of a specific experience."""
    template_name = 'experiences/experience_detail.html'
    context_object_name = 'experience'
    model = Experience
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        experience = self.get_object()
        
        # Check if the player is already participating in this experience
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            player_experience = PlayerExperience.objects.filter(player=player, experience=experience).first()
            context['player_experience'] = player_experience
            context['is_participating'] = player_experience is not None
        except PlayerProfile.DoesNotExist:
            context['is_participating'] = False
            
        # Add related zones and required powers
        context['zones'] = experience.associated_zones.all()
        context['required_powers'] = experience.required_powers.all()
        
        return context


class JoinExperienceView(LoginRequiredMixin, UpdateView):
    """Join an experience."""
    template_name = 'experiences/join_experience.html'
    
    def get(self, request, *args, **kwargs):
        experience = get_object_or_404(Experience, pk=self.kwargs['pk'])
        
        # Check if player already joined this experience
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            existing = PlayerExperience.objects.filter(player=player, experience=experience).exists()
            
            if existing:
                return redirect('experiences:experience_detail', pk=experience.id)
                
        except PlayerProfile.DoesNotExist:
            # Create player profile if it doesn't exist
            player = PlayerProfile.objects.create(user=self.request.user)
        
        return render(request, self.template_name, {
            'experience': experience,
            'success': False
        })
    
    def post(self, request, *args, **kwargs):
        experience = get_object_or_404(Experience, pk=self.kwargs['pk'])
        
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
        except PlayerProfile.DoesNotExist:
            player = PlayerProfile.objects.create(user=self.request.user)
            
        # Create player experience record
        player_exp, created = PlayerExperience.objects.get_or_create(
            player=player,
            experience=experience,
            defaults={
                'status': 'pull',
                'progress': 0
            }
        )
        
        if request.POST.get('redirect_to_detail', False):
            return redirect('experiences:experience_detail', pk=experience.id)
        
        return render(request, self.template_name, {
            'experience': experience,
            'success': True
        })


class UpdateExperienceStatusView(LoginRequiredMixin, UpdateView):
    """Update the status of a player's participation in an experience."""
    template_name = 'experiences/update_experience_status.html'
    
    def post(self, request, *args, **kwargs):
        experience_id = self.kwargs['experience_id']
        experience = get_object_or_404(Experience, pk=experience_id)
        
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            player_exp = get_object_or_404(PlayerExperience, player=player, experience=experience)
            
            # Update fields from form
            status = request.POST.get('status')
            progress = request.POST.get('progress')
            reflection_notes = request.POST.get('reflection_notes')
            
            if status:
                player_exp.status = status
                
            if progress:
                try:
                    player_exp.progress = int(progress)
                except (ValueError, TypeError):
                    pass
            
            if reflection_notes is not None:
                player_exp.reflection_notes = reflection_notes
                
            # If completed, set timestamp and award rewards
            if status == 'completed' and player_exp.completed_at is None:
                player_exp.completed_at = timezone.now()
                
                # Award experience points
                player.experience_points += experience.experience_reward
                player.save()
                
                # Record rewards in player_exp
                player_exp.experience_gained = experience.experience_reward
                player_exp.happiness_gained = experience.happiness_reward
            
            player_exp.save()
            
            # If AJAX request, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Experience status updated',
                    'player_exp': {
                        'status': player_exp.status,
                        'progress': player_exp.progress,
                        'status_display': player_exp.get_status_display()
                    }
                })
                
            # Otherwise redirect to the experience detail page
            return redirect('experiences:experience_detail', pk=experience_id)
            
        except (PlayerProfile.DoesNotExist, PlayerExperience.DoesNotExist):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Player experience not found'
                }, status=404)
                
            return redirect('experiences:experience_detail', pk=experience_id)


class PowerListView(LoginRequiredMixin, ListView):
    """List all powers available to the player."""
    template_name = 'experiences/power_list.html'
    context_object_name = 'powers'
    
    def get_queryset(self):
        """Return all powers that are public or owned by the player"""
        from experiences.models import Power, PlayerPower
        
        # Get all public powers
        queryset = Power.objects.filter(is_public=True)
        
        # Get filter parameters
        power_type = self.request.GET.get('type')
        sector_id = self.request.GET.get('sector')
        min_level = self.request.GET.get('level', 1)
        
        # Apply filters if provided
        if power_type:
            queryset = queryset.filter(power_type=power_type)
        
        if sector_id:
            queryset = queryset.filter(sector_id=sector_id)
        
        if min_level:
            try:
                min_level = int(min_level)
                # For powers, complexity can be used as a level requirement
                queryset = queryset.filter(complexity__lte=min_level*2)
            except (ValueError, TypeError):
                pass
        
        # If no powers found in database, generate some sample powers
        if not queryset.exists():
            from django.utils import timezone
            
            # Check if we need to create sample powers
            if Power.objects.count() == 0:
                # Create sample powers
                sample_powers = [
                    {
                        'name': 'Critical Thinking',
                        'description': 'The ability to analyze situations and arguments in a logical, unbiased manner.',
                        'power_type': 'skill',
                        'rarity': 3,
                        'complexity': 5,
                        'is_public': True,
                    },
                    {
                        'name': 'Research Methods',
                        'description': 'Knowledge of how to collect, analyze, and interpret data using scientific methods.',
                        'power_type': 'skill',
                        'rarity': 4,
                        'complexity': 6,
                        'is_public': True,
                    },
                    {
                        'name': 'Design Thinking',
                        'description': 'A human-centered approach to innovation that draws from the designer\'s toolkit to integrate the needs of people, the possibilities of technology, and the requirements for business success.',
                        'power_type': 'idea',
                        'rarity': 5,
                        'complexity': 7,
                        'is_public': True,
                    },
                    {
                        'name': 'Agile Project Management',
                        'description': 'An iterative approach to project management that helps teams deliver value to their customers faster.',
                        'power_type': 'technology',
                        'rarity': 6,
                        'complexity': 8,
                        'is_public': True,
                    },
                    {
                        'name': 'Public Speaking',
                        'description': 'The ability to speak effectively and confidently in front of groups.',
                        'power_type': 'skill',
                        'rarity': 4,
                        'complexity': 5,
                        'is_public': True,
                    },
                    {
                        'name': 'Sustainable Design',
                        'description': 'Approach to design that considers environmental impact and resource efficiency.',
                        'power_type': 'idea',
                        'rarity': 7,
                        'complexity': 8,
                        'is_public': True,
                    },
                ]
                
                for power_data in sample_powers:
                    Power.objects.create(**power_data)
                
                # Refresh queryset after creating sample powers
                queryset = Power.objects.filter(is_public=True)
                
                if power_type:
                    queryset = queryset.filter(power_type=power_type)
                
                if min_level:
                    try:
                        min_level = int(min_level)
                        queryset = queryset.filter(complexity__lte=min_level*2)
                    except (ValueError, TypeError):
                        pass
                
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add player powers to context"""
        context = super().get_context_data(**kwargs)
        
        # Add player powers (those the player has already acquired)
        try:
            player = PlayerProfile.objects.get(user=self.request.user)
            context['player_powers'] = player.powers.all().select_related('power')
            
            # Create a map of power IDs to player powers for easy lookup in template
            power_map = {}
            for pp in context['player_powers']:
                power_map[pp.power.id] = pp
            context['power_map'] = power_map
            
        except PlayerProfile.DoesNotExist:
            context['player_powers'] = []
            context['power_map'] = {}
            
        # Add sectors for filtering
        from zones.models import Sector
        context['sectors'] = Sector.objects.all()
        
        return context


class PowerDetailView(LoginRequiredMixin, DetailView):
    """Show details of a specific power."""
    template_name = 'experiences/power_detail.html'
    context_object_name = 'power'
    
    def get_object(self, queryset=None):
        # Stub implementation
        class StubPower:
            id = self.kwargs.get('pk')
            name = f"Power {self.kwargs.get('pk')}"
            description = "Power description placeholder"
            power_type = "skill"
            
            def get_power_type_display(self):
                return "Skill"
        
        return StubPower()

@login_required
def submit_experience(request):
    """View for users to submit new experiences"""
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            # Set default values and status
            experience.is_active = False  # Pending approval
            experience.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            messages.success(request, "Your experience has been submitted for review!")
            return redirect('experiences:experience_submitted')
    else:
        form = ExperienceForm()
    
    context = {
        'form': form,
        'google_maps_api_key': 'YOUR_API_KEY',  # You'll need to set up a Google Maps API key
    }
    return render(request, 'experiences/submit_experience.html', context)

@login_required
def experience_submitted(request):
    """Confirmation page after submission"""
    return render(request, 'experiences/experience_submitted.html')

@login_required
def experience_list(request):
    """List all approved experiences"""
    experiences = Experience.objects.filter(is_active=True)
    return render(request, 'experiences/experience_list.html', {'experiences': experiences})

@login_required
def experience_detail(request, pk):
    """View details of a specific experience"""
    experience = get_object_or_404(Experience, pk=pk, is_active=True)
    return render(request, 'experiences/experience_detail.html', {'experience': experience})

class ExperienceInstanceListView(LoginRequiredMixin, ListView):
    """List all available experience instances."""
    model = ExperienceInstance
    template_name = 'experiences/experience_instance_list.html'
    context_object_name = 'experience_instances'
    paginate_by = 12
    
    def get_queryset(self):
        """Return all available experience instances."""
        # Base queryset: exclude completed instances unless specifically requested
        queryset = ExperienceInstance.objects.all()
        
        # Filter by experience if provided
        experience_id = self.request.GET.get('experience_id')
        if experience_id:
            queryset = queryset.filter(experience_id=experience_id)
        
        # Filter by zone if provided
        zone_id = self.request.GET.get('zone_id')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        # Filter by start date if provided
        start_after = self.request.GET.get('start_after')
        if start_after:
            queryset = queryset.filter(start_time__gte=start_after)
        
        # Allow filtering by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by host if provided
        host_id = self.request.GET.get('host_id')
        if host_id:
            queryset = queryset.filter(host_id=host_id)
        
        # Sort by start time (upcoming first)
        return queryset.order_by('start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add current time for template comparisons
        context['now'] = timezone.now()
        
        # Add list of all experiences and zones for filter dropdowns
        context['all_experiences'] = Experience.objects.filter(is_active=True).order_by('name')
        context['all_zones'] = Zone.objects.all().order_by('name')
        
        return context


class ExperienceInstanceDetailView(LoginRequiredMixin, DetailView):
    """Display details of a specific experience instance."""
    model = ExperienceInstance
    template_name = 'experiences/experience_instance_detail.html'
    context_object_name = 'instance'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the instance
        instance = self.get_object()
        
        # Get participants
        context['participants'] = ExperienceParticipation.objects.filter(
            instance=instance
        ).select_related('player__user')
        
        # Check if the current user is participating
        player = get_object_or_404(PlayerProfile, user=self.request.user)
        context['user_participation'] = ExperienceParticipation.objects.filter(
            instance=instance,
            player=player
        ).first()
        
        # Add current time for template comparisons
        context['now'] = timezone.now()
        
        return context


class CreateExperienceInstanceView(LoginRequiredMixin, CreateView):
    """Create a new experience instance."""
    model = ExperienceInstance
    template_name = 'experiences/experience_instance_form.html'
    fields = [
        'experience', 'name', 'zone', 'start_time', 'end_time', 'frequency',
        'recurrence_rule', 'capacity', 'is_public', 'location_description',
        'meeting_point', 'resources_provided'
    ]
    success_url = reverse_lazy('experiences:instance_list')
    
    def form_valid(self, form):
        # Set the host to the current user's player
        form.instance.host = get_object_or_404(PlayerProfile, user=self.request.user)
        
        # Set initial status
        form.instance.status = 'scheduled'
        
        # Successfully created
        messages.success(self.request, 'Experience instance created successfully!')
        return super().form_valid(form)


class UpdateExperienceInstanceView(LoginRequiredMixin, UpdateView):
    """Update an existing experience instance."""
    model = ExperienceInstance
    template_name = 'experiences/experience_instance_form.html'
    fields = [
        'name', 'zone', 'start_time', 'end_time', 'frequency',
        'recurrence_rule', 'capacity', 'is_public', 'status',
        'location_description', 'meeting_point', 'resources_provided'
    ]
    
    def get_success_url(self):
        # Redirect back to the detail view of this instance
        return reverse('experiences:instance_detail', kwargs={'pk': self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the current user is the host
        instance = self.get_object()
        if instance.host.user != request.user:
            messages.error(request, "You don't have permission to edit this experience instance.")
            return redirect('experiences:instance_detail', pk=instance.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Successfully updated
        messages.success(self.request, 'Experience instance updated successfully!')
        return super().form_valid(form)


@login_required
def join_experience_instance(request, pk):
    """Join an experience instance."""
    instance = get_object_or_404(ExperienceInstance, pk=pk)
    player = get_object_or_404(PlayerProfile, user=request.user)
    
    # Check if already participating
    existing = ExperienceParticipation.objects.filter(
        instance=instance,
        player=player
    ).first()
    
    if request.method == 'POST':
        if existing:
            if existing.status == 'withdrawn':
                # Rejoin if previously withdrawn
                with transaction.atomic():
                    existing.status = 'joined'
                    existing.withdrawn_at = None
                    existing.save()
                    
                    # Update participant count
                    instance.current_participants += 1
                    instance.save()
                
                messages.success(request, 'You have rejoined this experience instance!')
            else:
                messages.info(request, 'You are already participating in this experience instance.')
        else:
            # Check if instance is full
            if instance.is_full:
                messages.error(request, 'This experience instance is already full.')
                return redirect('experiences:instance_detail', pk=instance.pk)
            
            # Check if instance is accepting new participants
            if instance.status not in ['scheduled', 'active']:
                messages.error(request, 'This experience instance is not accepting new participants.')
                return redirect('experiences:instance_detail', pk=instance.pk)
            
            # Create new participation
            with transaction.atomic():
                ExperienceParticipation.objects.create(
                    instance=instance,
                    player=player,
                    status='joined',
                    joined_at=timezone.now()
                )
                
                # Update participant count
                instance.current_participants += 1
                instance.save()
            
            messages.success(request, 'You have successfully joined this experience instance!')
    
    return redirect('experiences:instance_detail', pk=instance.pk)


@login_required
def withdraw_from_experience_instance(request, pk):
    """Withdraw from an experience instance."""
    instance = get_object_or_404(ExperienceInstance, pk=pk)
    player = get_object_or_404(PlayerProfile, user=request.user)
    
    # Get participation record
    participation = get_object_or_404(ExperienceParticipation, instance=instance, player=player)
    
    if request.method == 'POST':
        # Check if already withdrawn
        if participation.status == 'withdrawn':
            messages.info(request, 'You have already withdrawn from this experience instance.')
        elif participation.status == 'completed':
            messages.error(request, 'Cannot withdraw from a completed experience instance.')
        else:
            # Update participation and instance
            with transaction.atomic():
                participation.status = 'withdrawn'
                participation.withdrawn_at = timezone.now()
                participation.save()
                
                # Update participant count
                instance.current_participants -= 1
                instance.save()
            
            messages.success(request, 'You have withdrawn from this experience instance.')
    
    return redirect('experiences:instance_detail', pk=instance.pk)


@login_required
def advance_matrix_phase(request, pk):
    """Advance the matrix phase of an experience instance."""
    instance = get_object_or_404(ExperienceInstance, pk=pk)
    
    # Check if user is the host
    if instance.host.user != request.user:
        messages.error(request, 'Only the host can advance the matrix phase.')
        return redirect('experiences:instance_detail', pk=instance.pk)
    
    # Check if instance is active
    if instance.status != 'active':
        messages.error(request, 'Can only advance phase for active experience instances.')
        return redirect('experiences:instance_detail', pk=instance.pk)
    
    if request.method == 'POST':
        # Advance the phase
        instance.advance_matrix_phase()
        messages.success(request, f'Advanced to {instance.current_matrix_phase} phase!')
    
    return redirect('experiences:instance_detail', pk=instance.pk)