from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Avg, F, Q, Sum

from core.models import (
    Art, ArtParts, ArtStage, ArtTaxonomy, 
    TechTree, ArtMastery, UserArtStageProgress, 
    UserTechTreeProgress, PlayerProfile, PracticeSession
)
from core.services.art import ArtService, MasteryService, TechTreeService, PracticeService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:virtue_metrics_calculation]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]


class ArtPokedexView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the Art 'Pokedex' - a browsable catalog of arts
    """
    template_name = 'core/arts/pokedex.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = PlayerProfile.objects.get(user=user)
        
        # Get all available arts
        all_arts = ArtService.get_available_arts(
            user=user, 
            include_unlocked=True,
            economic_filter=False
        )
        
        # Add mastery information to each art
        user_masteries = ArtMastery.objects.filter(user=user)
        mastery_dict = {mastery.art.id: mastery for mastery in user_masteries}
        
        for art in all_arts:
            art.mastery = mastery_dict.get(art.id)
        
        # Paginate all arts
        paginator = Paginator(all_arts, 12)  # Show 12 arts per page
        page = self.request.GET.get('page')
        all_arts_paginated = paginator.get_page(page)
        
        # Get featured arts
        featured_arts = ArtService.get_featured_arts(limit=3)
        for art in featured_arts:
            art.mastery = mastery_dict.get(art.id)
        
        # Get taxonomies for filtering
        taxonomies = ArtTaxonomy.objects.filter(parent__isnull=True)
        
        # Get mastery summary
        mastery_summary = MasteryService.get_mastery_summary(user)
        
        context.update({
            'all_arts': all_arts_paginated,
            'featured_arts': featured_arts,
            'taxonomies': taxonomies,
            'mastery_summary': mastery_summary
        })
        
        return context


class ArtDetailView(LoginRequiredMixin, TemplateView):
    """
    View for displaying detailed information about a specific art
    """
    template_name = 'core/arts/art_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        art_id = self.kwargs.get('art_id')
        user = self.request.user
        
        # Get the art
        art = get_object_or_404(Art, id=art_id)
        
        # Get user's mastery for this art
        try:
            mastery = ArtMastery.objects.get(user=user, art=art)
        except ArtMastery.DoesNotExist:
            mastery = None
        
        # Get related arts
        related_arts = ArtService.get_related_arts(art)
        
        # If user has mastery, get practice history and other data
        practice_history = None
        practice_stats = None
        stage_progress = None
        
        if mastery:
            # Get practice history
            practice_history = PracticeService.get_practice_history(
                user=user, 
                art=art,
                limit=5
            )
            
            # Get practice stats
            practice_stats = PracticeService.get_practice_stats(user=user, art=art)
            
            # Get current stage progress
            current_stage = art.stages.filter(mastery_threshold__lte=mastery.mastery_level).last()
            if current_stage:
                try:
                    stage_progress = UserArtStageProgress.objects.get(
                        user=user,
                        art=art,
                        stage=current_stage
                    )
                except UserArtStageProgress.DoesNotExist:
                    pass
        
        # Prepare parts data
        parts = art.parts.all()
        if mastery:
            completed_parts = PracticeService.get_completed_parts(user=user, art=art)
            started_parts = PracticeService.get_started_parts(user=user, art=art)
            
            for part in parts:
                part.is_completed = part.id in completed_parts
                part.is_started = part.id in started_parts
        else:
            for part in parts:
                part.is_completed = False
                part.is_started = False
        
        # Prepare stages data
        stages = art.stages.all().order_by('mastery_threshold')
        if mastery:
            for stage in stages:
                stage.is_unlocked = stage.mastery_threshold <= mastery.mastery_level
        else:
            for stage in stages:
                stage.is_unlocked = False
        
        context.update({
            'art': art,
            'mastery': mastery,
            'related_arts': related_arts,
            'practice_history': practice_history,
            'practice_stats': practice_stats,
            'stage_progress': stage_progress
        })
        
        return context


class ArtDiscoverView(LoginRequiredMixin, View):
    """
    View for discovering (starting to learn) an art
    """
    def get(self, request, art_id):
        art = get_object_or_404(Art, id=art_id)
        user = request.user
        
        # Check if already has mastery
        if ArtMastery.objects.filter(user=user, art=art).exists():
            messages.info(request, f"You have already started learning {art.name}.")
            return redirect('core:art_detail', art_id=art_id)
        
        # Discover the art
        try:
            ArtService.discover_art(user=user, art=art)
            messages.success(request, f"You have started learning {art.name}!")
        except Exception as e:
            messages.error(request, str(e))
        
        return redirect('core:art_detail', art_id=art_id)


class LogPracticeView(LoginRequiredMixin, View):
    """
    View for logging practice sessions
    """
    def post(self, request, art_id):
        art = get_object_or_404(Art, id=art_id)
        user = request.user
        
        # Get mastery
        try:
            mastery = ArtMastery.objects.get(user=user, art=art)
        except ArtMastery.DoesNotExist:
            messages.error(request, "You haven't started learning this art yet.")
            return redirect('core:art_detail', art_id=art_id)
        
        # Get form data
        part_id = request.POST.get('part_id')
        duration = request.POST.get('duration')
        notes = request.POST.get('notes', '')
        complete_part = request.POST.get('complete_part') == 'on'
        
        # Validate part
        try:
            part = ArtParts.objects.get(id=part_id, art=art)
        except ArtParts.DoesNotExist:
            messages.error(request, "Invalid component selected.")
            return redirect('core:art_detail', art_id=art_id)
        
        # Validate duration
        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except (ValueError, TypeError):
            messages.error(request, "Invalid duration.")
            return redirect('core:art_detail', art_id=art_id)
        
        # Log practice session
        try:
            PracticeService.log_practice(
                user=user,
                art=art,
                part=part,
                duration=duration,
                notes=notes,
                mark_completed=complete_part
            )
            
            messages.success(request, f"Practice session for {part.name} recorded successfully!")
        except Exception as e:
            messages.error(request, str(e))
        
        return redirect('core:art_detail', art_id=art_id)


class TechTreeView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the tech tree
    """
    template_name = 'core/arts/tech_tree.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = PlayerProfile.objects.get(user=user)
        
        # Get tech tree levels and nodes
        tech_tree_levels = TechTreeService.get_tech_tree_by_levels(user=user)
        
        # Get tech tree stats
        tech_tree_stats = TechTreeService.get_tech_tree_stats(user=user)
        
        # Debug output to console
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        print("Tech Tree Levels JSON:")
        print(json.dumps(tech_tree_levels, cls=DjangoJSONEncoder, indent=2))
        print("Tech Tree Stats JSON:")
        print(json.dumps(tech_tree_stats, cls=DjangoJSONEncoder, indent=2))
        
        # Convert data to JSON for the template
        tech_tree_levels_json = json.dumps(tech_tree_levels, cls=DjangoJSONEncoder)
        tech_tree_stats_json = json.dumps(tech_tree_stats, cls=DjangoJSONEncoder)
        
        context.update({
            'tech_tree_levels': tech_tree_levels,
            'tech_tree_stats': tech_tree_stats,
            'tech_tree_levels_json': tech_tree_levels_json,
            'tech_tree_stats_json': tech_tree_stats_json,
            'user_profile': profile
        })
        
        return context


class TechTreeDetailView(LoginRequiredMixin, TemplateView):
    """
    View for displaying details about a specific tech tree node
    """
    template_name = 'core/arts/tech_tree_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tech_tree_id = self.kwargs.get('tech_tree_id')
        user = self.request.user
        
        # Get the tech tree
        tech_tree = get_object_or_404(TechTree, id=tech_tree_id)
        
        # Get user's progress for this tech tree
        try:
            progress = UserTechTreeProgress.objects.get(user=user, tech_tree=tech_tree)
        except UserTechTreeProgress.DoesNotExist:
            progress = None
        
        # Check if unlocked
        is_unlocked = TechTreeService.is_tech_tree_unlocked(user=user, tech_tree=tech_tree)
        
        # If not unlocked, redirect to tech tree view
        if not is_unlocked:
            messages.error(self.request, "This technology tree node is locked.")
            raise Http404("Tech tree node is locked")
        
        # Get prerequisites and their status
        prerequisites = []
        for prereq in tech_tree.parent_nodes.all():
            try:
                prereq_progress = UserTechTreeProgress.objects.get(user=user, tech_tree=prereq)
                met = prereq_progress.is_completed
            except UserTechTreeProgress.DoesNotExist:
                met = False
            
            prerequisites.append({
                'tech_tree': prereq,
                'is_met': met
            })
        
        # Get related arts (arts that contribute to this tech tree)
        related_arts = Art.objects.filter(id__in=tech_tree.unlocks_arts)
        
        # Add mastery information to each art
        user_masteries = ArtMastery.objects.filter(user=user, art__in=related_arts)
        mastery_dict = {mastery.art.id: mastery for mastery in user_masteries}
        
        for art in related_arts:
            art.mastery = mastery_dict.get(art.id)
        
        context.update({
            'tech_tree': tech_tree,
            'progress': progress,
            'prerequisites': prerequisites,
            'related_arts': related_arts
        })
        
        return context


class ArtMasteryDetailView(LoginRequiredMixin, TemplateView):
    """
    View for displaying detailed mastery stats for a specific art
    """
    template_name = 'core/arts/mastery_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mastery_id = self.kwargs.get('mastery_id')
        user = self.request.user
        
        # Get the mastery
        mastery = get_object_or_404(ArtMastery, id=mastery_id, user=user)
        art = mastery.art
        
        # Get practice history and stats
        practice_history = PracticeService.get_practice_history(user=user, art=art)
        practice_stats = PracticeService.get_practice_stats(user=user, art=art)
        
        # Prepare parts data
        parts = art.parts.all()
        completed_parts = PracticeService.get_completed_parts(user=user, art=art)
        started_parts = PracticeService.get_started_parts(user=user, art=art)
        
        for part in parts:
            part.is_completed = part.id in completed_parts
            part.is_started = part.id in started_parts
        
        # Prepare stages data
        stages = art.stages.all().order_by('mastery_threshold')
        for stage in stages:
            stage.is_unlocked = stage.mastery_threshold <= mastery.mastery_level
            
            if stage.is_unlocked:
                try:
                    stage.progress = UserArtStageProgress.objects.get(
                        user=user,
                        art=art,
                        stage=stage
                    )
                except UserArtStageProgress.DoesNotExist:
                    stage.progress = None
        
        context.update({
            'mastery': mastery,
            'art': art,
            'practice_history': practice_history,
            'practice_stats': practice_stats,
            'parts': parts,
            'stages': stages
        })
        
        return context


class ArtMasteryStatsView(LoginRequiredMixin, TemplateView):
    """
    View for displaying overall mastery stats across all arts
    """
    template_name = 'core/arts/mastery_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get mastery summary
        mastery_summary = MasteryService.get_mastery_summary(user)
        
        # Get all user masteries
        masteries = ArtMastery.objects.filter(user=user).order_by('-mastery_level')
        
        # Get practice statistics
        practice_stats = PracticeService.get_overall_practice_stats(user)
        
        context.update({
            'mastery_summary': mastery_summary,
            'masteries': masteries,
            'practice_stats': practice_stats
        })
        
        return context


class ArtMasteryDashboardView(LoginRequiredMixin, TemplateView):
    """
    View for the Art Mastery Dashboard, a central hub for tracking and planning art practice.
    """
    template_name = 'core/arts/mastery_dashboard.html'
    
    def get_taxonomy_descendants(self, taxonomy, include_self=True):
        """
        Helper method to get all descendants of a taxonomy node recursively.
        
        Args:
            taxonomy: The ArtTaxonomy object
            include_self: Whether to include the taxonomy itself in the results
            
        Returns:
            A list of ArtTaxonomy objects
        """
        result = [taxonomy] if include_self else []
        children = ArtTaxonomy.objects.filter(parent=taxonomy)
        for child in children:
            result.extend(self.get_taxonomy_descendants(child))
        return result
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get mastery summary
        context['mastery_summary'] = MasteryService.get_mastery_summary(user)
        
        # Get top masteries
        context['top_masteries'] = ArtMastery.objects.filter(
            user=user
        ).order_by('-mastery_level')[:6]
        
        # Get today's practice sessions
        today = timezone.now().date()
        context['scheduled_practices'] = PracticeSession.objects.filter(
            user=user,
            started_at__date=today,
            completed=False
        ).order_by('started_at')
        
        # Get practice history
        practice_history = PracticeSession.objects.filter(
            user=user,
            completed=True
        ).values('started_at__date').annotate(count=Count('id'))
        
        # Format practice days for JS consumption
        practice_days = {}
        for practice in practice_history:
            date_str = practice['started_at__date'].strftime('%Y-%m-%d')
            practice_days[date_str] = practice['count']
        
        # Get mastery categories for radar chart
        taxonomies = ArtTaxonomy.objects.filter(level=1)  # Top-level categories
        mastery_categories = []
        
        for taxonomy in taxonomies:
            # Get all taxonomies in this category tree using our helper method
            taxonomy_descendants = self.get_taxonomy_descendants(taxonomy)
            
            # Get all arts in this category that the user has mastery in
            arts_in_category = Art.objects.filter(
                taxonomy__in=taxonomy_descendants,
                masteries__user=user
            )
            
            # Calculate average mastery
            masteries = ArtMastery.objects.filter(
                user=user,
                art__in=arts_in_category
            )
            
            avg_mastery = 0
            if masteries.exists():
                avg_mastery = sum(m.mastery_level for m in masteries) / masteries.count()
            
            mastery_categories.append({
                'name': taxonomy.name,
                'average_mastery': avg_mastery
            })
        
        # Get recent practice activities
        recent_activities = []
        recent_practices = PracticeSession.objects.filter(
            user=user
        ).select_related('art', 'part').order_by('-created_at')[:5]
        
        for practice in recent_practices:
            activity = {
                'icon': 'palette',
                'title': f'Practiced {practice.art.name}',
                'description': f'Worked on {practice.part.name} for {practice.duration_minutes} minutes',
                'timestamp': practice.started_at,
                'related_virtues': []
            }
            
            # Add related virtues if available
            if practice.art.improved_virtues:
                activity['related_virtues'] = list(practice.art.improved_virtues.keys())
            
            recent_activities.append(activity)
        
        # Generate practice recommendations based on mastery level and practice history
        recommendations = self.generate_practice_recommendations(user)
        
        # Get virtue connections
        virtue_connections = {}
        user_masteries = ArtMastery.objects.filter(user=user).select_related('art')
        
        for mastery in user_masteries:
            if mastery.art.improved_virtues:
                for virtue, impact in mastery.art.improved_virtues.items():
                    if virtue not in virtue_connections:
                        virtue_connections[virtue] = []
                    
                    virtue_connections[virtue].append({
                        'art': mastery.art.name,
                        'impact': impact
                    })
        
        # Calculate practice summary
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_practices = PracticeSession.objects.filter(
            user=user,
            started_at__gte=month_start
        )
        
        practice_summary = {
            'month_count': month_practices.count(),
            'month_hours': sum(p.duration_minutes for p in month_practices) / 60
        }
        
        # Get user arts for form
        user_arts = Art.objects.filter(masteries__user=user)
        
        context.update({
            'mastery_summary': context['mastery_summary'],
            'top_masteries': context['top_masteries'],
            'scheduled_practices': context['scheduled_practices'],
            'practice_days': practice_days,
            'mastery_categories': mastery_categories,
            'recent_activities': recent_activities,
            'recommended_practices': recommendations,
            'virtue_connections': virtue_connections,
            'practice_summary': practice_summary,
            'user_arts': user_arts
        })
        
        return context
    
    def generate_practice_recommendations(self, user):
        """
        Generate practice recommendations based on various factors:
        1. Arts that haven't been practiced recently
        2. Arts with low mastery level compared to user average
        3. Arts that improve virtues where the user is weak
        """
        recommendations = []
        
        # Get user's mastery data
        masteries = ArtMastery.objects.filter(user=user).select_related('art')
        
        if not masteries.exists():
            return recommendations
        
        # Calculate average mastery
        avg_mastery = sum(m.mastery_level for m in masteries) / masteries.count()
        
        # Get user's virtue levels
        player_profile = PlayerProfile.objects.get(user=user)
        virtue_levels = {}
        
        if hasattr(player_profile, 'happiness'):
            happiness = player_profile.happiness
            if hasattr(happiness, 'virtue_levels'):
                virtue_levels = happiness.virtue_levels
        
        # Find lowest virtues
        weak_virtues = []
        if virtue_levels:
            sorted_virtues = sorted(virtue_levels.items(), key=lambda x: x[1])
            weak_virtues = [v[0] for v in sorted_virtues[:2]]  # Two weakest virtues
        
        # Create recommendations
        for mastery in masteries:
            priority = 0
            reasons = []
            
            # Factor 1: Not practiced recently
            if mastery.last_practiced:
                days_since = (timezone.now() - mastery.last_practiced).days
                if days_since > 7:
                    priority += 1
                    reasons.append(f"Not practiced in {days_since} days")
            else:
                priority += 1
                reasons.append("Never practiced")
            
            # Factor 2: Low mastery compared to average
            if mastery.mastery_level < avg_mastery - 1:
                priority += 1
                reasons.append("Below your average mastery level")
            
            # Factor 3: Improves weak virtues
            improves_virtues = []
            if mastery.art.improved_virtues and weak_virtues:
                for virtue in weak_virtues:
                    if virtue in mastery.art.improved_virtues:
                        improves_virtues.append(virtue)
                        priority += 1
                        reasons.append(f"Improves {virtue} (one of your weaker virtues)")
            
            if priority > 0:
                # Get current or next part to practice
                current_part = mastery.current_part
                if not current_part:
                    # Find first part if no current part
                    try:
                        current_part = ArtParts.objects.filter(art=mastery.art).order_by('order_index').first()
                    except ArtParts.DoesNotExist:
                        continue
                
                recommendations.append({
                    'art': mastery.art,
                    'part': current_part,
                    'priority': priority,
                    'reasons': reasons,
                    'improves_virtues': improves_virtues,
                    'duration': 30  # Default 30 minutes
                })
        
        # Sort by priority (highest first)
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations 