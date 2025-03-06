from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, Optional, List
from django.db.models import Sum, Count, Avg, Min, Max, F

from core.models import (
    Art,
    ArtParts,
    ArtMastery,
    PlayerProfile,
    PracticeSession,
    UserArtStageProgress
)

from .mastery_service import MasteryService

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:CHECK_PATTERN:experience_progression]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

User = get_user_model()

class PracticeService:
    """
    Service for managing art practice sessions.
    """
    
    @staticmethod
    def log_practice(user, art, part, duration, notes='', mark_completed=False):
        """
        Log a practice session for a user.
        
        Args:
            user: The user practicing the art
            art: The Art object being practiced
            part: The ArtParts object being practiced
            duration: Duration of practice in minutes
            notes: Optional notes about the practice session
            mark_completed: Whether to mark the part as completed
            
        Returns:
            The created PracticeSession instance
        """
        # Ensure user has mastery for this art
        mastery, _ = ArtMastery.objects.get_or_create(user=user, art=art)
        
        with transaction.atomic():
            # Create practice session
            session = PracticeSession.objects.create(
                user=user,
                art=art,
                part=part,
                duration=duration,
                notes=notes
            )
            
            # Update mastery history
            current_history = mastery.practice_history or []
            current_history.append({
                'date': timezone.now().isoformat(),
                'duration': duration,
                'part_id': str(part.id),
                'part_name': part.name
            })
            
            mastery.practice_history = current_history
            
            # If marking as completed and not already completed
            if mark_completed:
                completed_parts = mastery.completed_parts or []
                if str(part.id) not in completed_parts:
                    completed_parts.append(str(part.id))
                    mastery.completed_parts = completed_parts
            
            # Award XP for practice (1 XP per minute)
            mastery.experience_points = F('experience_points') + duration
            
            # Save changes
            mastery.save()
            
            # Update mastery level based on new XP
            MasteryService.update_mastery_level(mastery)
            
            return session
    
    @staticmethod
    def get_practice_history(user, art=None, limit=None):
        """
        Get practice history for a user, optionally filtered by art.
        
        Args:
            user: The user to get history for
            art: Optional Art object to filter history
            limit: Optional limit on number of sessions to return
            
        Returns:
            QuerySet of PracticeSession objects
        """
        query = PracticeSession.objects.filter(user=user)
        
        if art:
            query = query.filter(art=art)
        
        query = query.order_by('-created_at')
        
        if limit:
            query = query[:limit]
            
        return query
    
    @staticmethod
    def get_practice_stats(user, art=None):
        """
        Get practice statistics for a user, optionally filtered by art.
        
        Args:
            user: The user to get stats for
            art: Optional Art object to filter stats
            
        Returns:
            Dictionary with practice statistics
        """
        query = PracticeSession.objects.filter(user=user)
        
        if art:
            query = query.filter(art=art)
            mastery = ArtMastery.objects.get(user=user, art=art)
            total_parts = art.parts.count()
            completed_parts = len(mastery.completed_parts or [])
        else:
            # For all arts
            total_parts = ArtParts.objects.filter(art__in=Art.objects.filter(
                id__in=PracticeSession.objects.filter(user=user).values_list('art', flat=True).distinct()
            )).count()
            
            completed_parts = sum(
                len(m.completed_parts or []) 
                for m in ArtMastery.objects.filter(user=user)
            )
        
        stats = query.aggregate(
            total_sessions=Count('id'),
            total_minutes=Sum('duration'),
            avg_duration=Avg('duration'),
            longest_session=Max('duration'),
            shortest_session=Min('duration'),
            last_practice=Max('created_at')
        )
        
        stats.update({
            'total_parts': total_parts,
            'completed_parts': completed_parts,
            'completion_percentage': (completed_parts / total_parts * 100) if total_parts > 0 else 0
        })
        
        return stats
    
    @staticmethod
    def get_overall_practice_stats(user):
        """
        Get overall practice statistics across all arts.
        
        Args:
            user: The user to get stats for
            
        Returns:
            Dictionary with overall practice statistics
        """
        return PracticeService.get_practice_stats(user)
    
    @staticmethod
    def get_completed_parts(user, art):
        """
        Get IDs of parts completed by a user for an art.
        
        Args:
            user: The user
            art: The Art object
            
        Returns:
            Set of part IDs completed by the user
        """
        try:
            mastery = ArtMastery.objects.get(user=user, art=art)
            completed_parts = mastery.completed_parts or []
            return {part_id for part_id in completed_parts}
        except ArtMastery.DoesNotExist:
            return set()
    
    @staticmethod
    def get_started_parts(user, art):
        """
        Get IDs of parts started (practiced at least once) by a user for an art.
        
        Args:
            user: The user
            art: The Art object
            
        Returns:
            Set of part IDs started by the user
        """
        practiced_part_ids = set(
            PracticeSession.objects.filter(user=user, art=art)
            .values_list('part_id', flat=True)
        )
        
        return practiced_part_ids
    
    @staticmethod
    def validate_practice(user, art, part, min_duration=None, completion_criteria=None):
        """
        Validate if a practice session meets certain criteria.
        
        Args:
            user: The user
            art: The Art object
            part: The ArtParts object
            min_duration: Minimum total duration required (across all sessions)
            completion_criteria: Custom function to check if practice meets criteria
            
        Returns:
            Boolean indicating if practice is valid according to criteria
        """
        # Get all practice sessions for this part
        sessions = PracticeSession.objects.filter(user=user, art=art, part=part)
        
        if not sessions.exists():
            return False
        
        # Check minimum duration
        if min_duration:
            total_duration = sessions.aggregate(total=Sum('duration'))['total'] or 0
            if total_duration < min_duration:
                return False
        
        # Apply custom criteria if provided
        if completion_criteria and callable(completion_criteria):
            return completion_criteria(sessions)
        
        return True
    
    @staticmethod
    def get_practice_stats(user, art=None, days=30):
        """
        Get practice statistics for a user.
        
        Args:
            user: The User object or ID
            art: Optional Art object or ID to filter by
            days: Number of days to look back
            
        Returns:
            Dict: Practice statistics
        """
        if not isinstance(user, User):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                raise ValueError(f"User with ID {user} does not exist")
        
        # Define the period to analyze
        cutoff_date = (timezone.now() - timezone.timedelta(days=days))
        
        # Get all masteries or filter by art
        masteries_query = ArtMastery.objects.filter(user=user)
        if art:
            if not isinstance(art, Art):
                try:
                    art = Art.objects.get(id=art)
                except Art.DoesNotExist:
                    raise ValueError(f"Art with ID {art} does not exist")
            
            masteries_query = masteries_query.filter(art=art)
        
        masteries = list(masteries_query)
        
        # Initialize stats
        stats = {
            'total_sessions': 0,
            'total_minutes': 0,
            'sessions_by_day': {},
            'minutes_by_art': {},
            'streak_days': 0,
            'longest_session': 0,
            'validated_parts': 0,
            'practice_methods': {}
        }
        
        # Initialize days for the streak calendar
        for i in range(days):
            day = (timezone.now() - timezone.timedelta(days=i)).date().isoformat()
            stats['sessions_by_day'][day] = 0
        
        # Process each mastery
        for mastery in masteries:
            if not mastery.practice_history:
                continue
                
            art_minutes = 0
            art_sessions = 0
            art_name = mastery.art.name
            
            # Count completed parts
            stats['validated_parts'] += len(mastery.completed_parts or [])
            
            # Analyze practice sessions
            for session in mastery.practice_history:
                session_time = session.get('timestamp', '')
                if not session_time:
                    continue
                    
                try:
                    session_datetime = timezone.datetime.fromisoformat(session_time)
                    if session_datetime.tzinfo is None:
                        # Add UTC if no timezone specified
                        session_datetime = session_datetime.replace(tzinfo=timezone.utc)
                        
                    # Skip if before cutoff date
                    if session_datetime < cutoff_date:
                        continue
                        
                    # Count this session
                    stats['total_sessions'] += 1
                    art_sessions += 1
                    
                    # Add minutes
                    minutes = session.get('duration_minutes', 0)
                    stats['total_minutes'] += minutes
                    art_minutes += minutes
                    
                    # Track longest session
                    stats['longest_session'] = max(stats['longest_session'], minutes)
                    
                    # Track by day for streak calculation
                    day = session_datetime.date().isoformat()
                    if day in stats['sessions_by_day']:
                        stats['sessions_by_day'][day] += 1
                    
                    # Track practice method if available
                    if 'part_id' in session:
                        try:
                            part = ArtParts.objects.get(id=session['part_id'])
                            method = part.get_practice_method_display()
                            if method not in stats['practice_methods']:
                                stats['practice_methods'][method] = 0
                            stats['practice_methods'][method] += 1
                        except ArtParts.DoesNotExist:
                            pass
                            
                except (ValueError, TypeError):
                    continue
            
            # Add to art-specific stats
            if art_sessions > 0:
                stats['minutes_by_art'][art_name] = art_minutes
        
        # Calculate streak
        stats['streak_days'] = PracticeService.calculate_streak(stats['sessions_by_day'])
        
        return stats
    
    @staticmethod
    def calculate_streak(sessions_by_day):
        """
        Calculate the current practice streak in days.
        
        Args:
            sessions_by_day: Dictionary mapping days to session counts
            
        Returns:
            int: Current streak in days
        """
        # Sort days in descending order (newest first)
        sorted_days = sorted(sessions_by_day.keys(), reverse=True)
        
        # Check if practiced today
        if not sorted_days or sessions_by_day[sorted_days[0]] == 0:
            return 0
        
        # Count streak days
        streak = 1  # Start with today
        last_day = timezone.datetime.fromisoformat(sorted_days[0]).date()
        
        for i in range(1, len(sorted_days)):
            day = timezone.datetime.fromisoformat(sorted_days[i]).date()
            expected_day = last_day - timezone.timedelta(days=1)
            
            # If this is the expected previous day and has sessions
            if day == expected_day and sessions_by_day[sorted_days[i]] > 0:
                streak += 1
                last_day = day
            else:
                break
                
        return streak 